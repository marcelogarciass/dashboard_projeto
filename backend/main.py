from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from jira import JIRA
import toml
import os
from datetime import datetime
import numpy as np

app = FastAPI(title="Jira Dashboard API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration & Auth ---
SECRETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")

def get_jira_client():
    try:
        if os.path.exists(SECRETS_PATH):
            secrets = toml.load(SECRETS_PATH)
            return JIRA(
                server=secrets["jira"]["url"],
                basic_auth=(secrets["jira"]["username"], secrets["jira"]["token"])
            )
        else:
            # Fallback to env vars if needed
            raise FileNotFoundError("Secrets file not found")
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        return None

# --- Data Cache (Simple In-Memory for MVP) ---
# In a real production app, use Redis or similar.
CACHE = {
    "data": None,
    "last_updated": None
}
CACHE_TTL = 3600  # 1 hour

def get_data():
    now = datetime.now()
    if CACHE["data"] is not None and CACHE["last_updated"] is not None:
        if (now - CACHE["last_updated"]).total_seconds() < CACHE_TTL:
            return CACHE["data"]

    jira = get_jira_client()
    if not jira:
        raise HTTPException(status_code=500, detail="Could not connect to Jira")

    print("Fetching data from Jira...")
    jql = 'statusCategory != Done OR created >= -730d ORDER BY created DESC'
    fields = "summary,assignee,status,created,project,customfield_10031,customfield_10020,duedate,priority,issuetype,resolutiondate,updated,timeoriginalestimate,timespent,components,labels"
    
    issues = jira.search_issues(jql, maxResults=0, fields=fields)
    
    data = []
    for issue in issues:
        assignee = issue.fields.assignee.displayName if issue.fields.assignee else 'Não Atribuído'
        story_points = getattr(issue.fields, 'customfield_10031', 0) or 0
        sprint_field = getattr(issue.fields, 'customfield_10020', None)
        sprint_name = sprint_field[0].name if sprint_field else 'Backlog'
        
        data.append({
            'Chave': issue.key,
            'Resumo': issue.fields.summary,
            'Tipo': issue.fields.issuetype.name,
            'Status': issue.fields.status.name,
            'Prioridade': issue.fields.priority.name if issue.fields.priority else 'Medium',
            'Responsável': assignee,
            'Projeto': issue.fields.project.name,
            'Criado': issue.fields.created,
            'Resolvido': issue.fields.resolutiondate,
            'Story Points': float(story_points),
            'Sprint': sprint_name,
            'Módulo': issue.fields.components[0].name if issue.fields.components else 'Geral',
            'Data Entrega': issue.fields.duedate
        })
    
    df = pd.DataFrame(data)
    
    # Pre-processing
    df['Criado'] = pd.to_datetime(df['Criado'], utc=True).dt.tz_convert(None)
    df['Resolvido'] = pd.to_datetime(df['Resolvido'], utc=True).dt.tz_convert(None)
    df['Data Entrega'] = pd.to_datetime(df['Data Entrega'])
    
    # Status Categories
    STATUS_DONE = ['Concluído', 'Done', 'Finalizado', 'Resolvido', 'Closed']
    df['Status_Category'] = df['Status'].apply(lambda x: 'Done' if x in STATUS_DONE else 'Active')
    
    CACHE["data"] = df
    CACHE["last_updated"] = now
    return df

# --- Endpoints ---

class FilterParams(BaseModel):
    projects: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    types: Optional[List[str]] = None
    period: str = "Tudo" # Tudo, Este Mês, Mês Passado, etc.

@app.get("/api/filters")
def get_filters():
    df = get_data()
    return {
        "projects": sorted(df['Projeto'].unique().tolist()),
        "statuses": sorted(df['Status'].unique().tolist()),
        "types": sorted(df['Tipo'].unique().tolist()),
        "assignees": sorted(df['Responsável'].unique().tolist())
    }

@app.post("/api/dashboard")
def get_dashboard_data(filters: FilterParams):
    df = get_data()
    
    # Apply Filters
    if filters.projects and "Todos" not in filters.projects:
        df = df[df['Projeto'].isin(filters.projects)]
    if filters.statuses:
        df = df[df['Status'].isin(filters.statuses)]
    if filters.types:
        df = df[df['Tipo'].isin(filters.types)]
        
    # Time Filtering (Simplified for this example)
    today = datetime.today()
    if filters.period == "Este Mês":
        df = df[df['Criado'] >= today.replace(day=1)]
    # ... add other period logic as needed
    
    # --- KPIs ---
    total_issues = len(df)
    active_issues = len(df[df['Status_Category'] == 'Active'])
    done_issues = len(df[df['Status_Category'] == 'Done'])
    bugs = len(df[df['Tipo'].isin(['Bug', 'Bug Report'])])
    
    # --- Charts Data Preparation ---
    
    # 1. Status by Project
    status_by_project = df.groupby(['Projeto', 'Status']).size().reset_index(name='count')
    
    # 2. Burndown (Burnup: Scope vs Delivered)
    df_burn = df.sort_values('Criado')
    df_burn['count'] = 1
    df_burn['cumsum'] = df_burn['count'].cumsum()
    
    # Scope Line
    scope_data = df_burn[['Criado', 'cumsum']].rename(columns={'cumsum': 'scope'}).to_dict(orient='records')
    
    # Delivered Line
    df_done = df[df['Status_Category'] == 'Done'].copy()
    delivered_data = []
    if not df_done.empty:
        df_done = df_done.sort_values('Resolvido').dropna(subset=['Resolvido'])
        df_done['count'] = 1
        df_done['cumsum_done'] = df_done['count'].cumsum()
        delivered_data = df_done[['Resolvido', 'cumsum_done']].rename(columns={'Resolvido': 'Criado', 'cumsum_done': 'delivered'}).to_dict(orient='records')
    
    # Merge for chart (Simplified merge by concatenating and letting frontend handle x-axis or just sending two series)
    # Ideally, we align them on a common timeline. For simplicity, we'll send two lists or a combined list if we had a common date index.
    # Let's just send a combined list sorted by date for easier frontend consumption, or separate series.
    # Recharts prefers a single array with keys like { date: '...', scope: 10, delivered: 5 }
    
    # Create a common timeline
    timeline_dates = sorted(list(set(df['Criado'].tolist() + df_done['Resolvido'].tolist())))
    burndown_data = []
    
    current_scope = 0
    current_delivered = 0
    
    # Pre-calculate lookups
    scope_lookup = df_burn.set_index('Criado')['cumsum'].to_dict() # This might miss duplicates, better to use forward fill logic
    # Better approach: resample by day
    
    # Resample Scope
    df_burn_daily = df_burn.set_index('Criado').resample('D')['count'].sum().cumsum().reset_index()
    df_burn_daily.columns = ['date', 'scope']
    
    # Resample Delivered
    if not df_done.empty:
        df_done_daily = df_done.set_index('Resolvido').resample('D')['count'].sum().cumsum().reset_index()
        df_done_daily.columns = ['date', 'delivered']
        
        # Merge
        df_merged = pd.merge(df_burn_daily, df_done_daily, on='date', how='outer').sort_values('date').fillna(method='ffill').fillna(0)
    else:
        df_merged = df_burn_daily
        df_merged['delivered'] = 0
        
    burndown_data = df_merged.to_dict(orient='records')
    
    # 3. Type Distribution
    type_dist = df['Tipo'].value_counts().reset_index()
    type_dist.columns = ['name', 'value']
    
    # 4. Team Load
    team_load = df[df['Status_Category'] == 'Active'].groupby('Responsável').agg(
        issues=('Chave', 'count'),
        points=('Story Points', 'sum')
    ).reset_index().sort_values('points', ascending=False)
    
    return {
        "kpis": {
            "total": total_issues,
            "active": active_issues,
            "done": done_issues,
            "bugs": bugs
        },
        "charts": {
            "status_by_project": status_by_project.to_dict(orient='records'),
            "burndown": burndown_data,
            "type_distribution": type_dist.to_dict(orient='records'),
            "team_load": team_load.to_dict(orient='records')
        },
        "raw_subset": df.head(50).fillna('').to_dict(orient='records') # Preview
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
