import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jira import JIRA
import re
from datetime import datetime
from fpdf import FPDF
import base64

# --- Configuração da Página ---
st.set_page_config(page_title="Gestão de Projetos & Eficiência", layout="wide", page_icon="📈")

# --- Custom CSS (Clean Corporate Theme) ---
st.markdown("""
<!-- Tailwind CDN & Config -->
<script src="https://cdn.tailwindcss.com"></script>
<script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'brand-blue': '#0047AB', /* Cobalt Blue - Strong Corporate */
            'brand-bg': '#F4F5F7',   /* Light Gray Background */
            'brand-text': '#172B4D', /* Dark Navy Text */
            'card-bg': '#FFFFFF',
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
          }
        }
      }
    }
</script>

<style>
    /* Import Google Fonts - Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Streamlit Global Overrides */
    .stApp {
        background-color: #F4F5F7;
        color: #172B4D;
        font-family: 'Inter', sans-serif;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        color: #0047AB;
        text-transform: none;
        letter-spacing: normal;
        background: none;
        -webkit-text-fill-color: initial;
        text-shadow: none;
    }
    
    /* Metrics Cards - Clean White Style */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DFE1E6;
        border-left: 4px solid #0047AB;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #0047AB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    div[data-testid="stMetric"] label {
        color: #5E6C84 !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #172B4D !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        text-shadow: none;
    }

    /* Tabs - Pills Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 0;
        border-radius: 0;
        border-bottom: 2px solid #DFE1E6;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 4px;
        color: #5E6C84;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        border: none;
        background-color: transparent;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E6F0FF;
        color: #0047AB !important;
        border-bottom: 2px solid #0047AB;
        border-radius: 4px 4px 0 0;
    }
    
    /* Adjust Sidebar to match */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #DFE1E6;
    }
</style>
""", unsafe_allow_html=True) 

# --- Configurações do Jira ---
# Credenciais movidas para .streamlit/secrets.toml

# --- Função de Carregamento de Dados do Jira ---
@st.cache_data(ttl=3600) # Cache de 1 hora
def load_data_jira():
    try:
        jira = JIRA(server=st.secrets["jira"]["url"], basic_auth=(st.secrets["jira"]["username"], st.secrets["jira"]["token"]))
        
        # JQL Query: Busca tickets ABERTOS (sem limite de data) e FECHADOS (últimos 2 anos)
        jql = 'statusCategory != Done OR created >= -730d ORDER BY created DESC'
        
        # Adicionado campos extras para o novo dashboard
        fields = "summary,assignee,status,created,project,customfield_10026,customfield_10020,duedate,priority,issuetype,resolutiondate,updated,timeoriginalestimate,timespent,components,labels"
        
        # maxResults=0 garante retorno de TODOS os tickets (bypass paginação padrão)
        issues = jira.search_issues(jql, maxResults=0, fields=fields)
        
        data = []
        for issue in issues:
            # Extração segura de campos
            assignee = issue.fields.assignee.displayName if issue.fields.assignee else 'Não Atribuído'
            story_points = getattr(issue.fields, 'customfield_10026', 0)
            if story_points is None: story_points = 0
            
            # Parsing de Sprint
            sprint_raw = getattr(issue.fields, 'customfield_10020', None)
            sprint_name = 'Backlog' # Default
            if sprint_raw:
                try:
                    sprint_data = sprint_raw[0]
                    if hasattr(sprint_data, 'name'):
                        sprint_name = sprint_data.name
                    else:
                        match = re.search(r'name=([^,]+)', str(sprint_data))
                        if match:
                            sprint_name = match.group(1)
                except Exception:
                    pass
            
            # Tratamento de datas
            created = pd.to_datetime(issue.fields.created).replace(tzinfo=None) if issue.fields.created else None
            duedate = pd.to_datetime(issue.fields.duedate).replace(tzinfo=None) if issue.fields.duedate else None
            resolutiondate = pd.to_datetime(issue.fields.resolutiondate).replace(tzinfo=None) if issue.fields.resolutiondate else None
            updated = pd.to_datetime(issue.fields.updated).replace(tzinfo=None) if issue.fields.updated else None

            # Campos adicionais
            estimate = issue.fields.timeoriginalestimate if hasattr(issue.fields, 'timeoriginalestimate') and issue.fields.timeoriginalestimate else 0
            spent = issue.fields.timespent if hasattr(issue.fields, 'timespent') and issue.fields.timespent else 0
            
            components = [c.name for c in issue.fields.components] if hasattr(issue.fields, 'components') and issue.fields.components else []
            module = components[0] if components else 'Geral'
            
            labels = issue.fields.labels if hasattr(issue.fields, 'labels') and issue.fields.labels else []
            client_tag = next((l for l in labels if l.startswith('CLI_')), 'Interno') # Exemplo de tag de cliente

            data.append({
                'Chave': issue.key,
                'Resumo': issue.fields.summary,
                'Responsável': assignee,
                'Status': issue.fields.status.name,
                'Tipo': issue.fields.issuetype.name,
                'Prioridade': issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'Medium',
                'Projeto': issue.fields.project.name,
                'Criado': created,
                'Resolvido': resolutiondate,
                'Data Entrega': duedate,
                'Atualizado': updated,
                'Story Points': story_points,
                'Sprint': sprint_name,
                'Estimativa (s)': estimate,
                'Tempo Gasto (s)': spent,
                'Módulo': module,
                'Cliente': client_tag,
                'Labels': labels
            })
            
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Erro ao conectar ao Jira: {e}")
        return pd.DataFrame()

# --- Carregamento Inicial ---
with st.spinner('Conectando ao Jira e analisando dados...'):
    df = load_data_jira()

if df.empty:
    st.warning("Nenhum dado encontrado ou erro na conexão.")
    st.stop()

# --- Processamento de Métricas Avançadas ---
today = pd.to_datetime('today').normalize()
status_concluidos = ['Concluído', 'Done', 'Finalizado', 'Closed', 'Resolvido']

# 1. Identificar Atrasos
def verificar_atraso(row):
    if row['Status'] in status_concluidos:
        return False
    if pd.notnull(row['Data Entrega']) and row['Data Entrega'] < today:
        return True
    return False

df['Atrasado'] = df.apply(verificar_atraso, axis=1)

# 2. Calcular Lead Time (Dias Corridos)
df['Lead Time'] = (df['Resolvido'] - df['Criado']).dt.days
df['Lead Time'] = df['Lead Time'].fillna(0) # Para não quebrar cálculos, mas filtrar depois

# --- Sidebar (Filtros Avançados) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Jira_Logo.svg/1200px-Jira_Logo.svg.png", width=100)
st.sidebar.markdown("### 🔍 Filtros Avançados")

# 1. Filtro de Tempo (Presets)
with st.sidebar.expander("📅 Período de Análise", expanded=True):
    periodo_opcao = st.selectbox("Preset de Tempo", ["Tudo", "Este Mês", "Mês Passado", "Último Trimestre", "Este Ano", "Personalizado"])
    
    today = datetime.today()
    if periodo_opcao == "Este Mês":
        start_date = today.replace(day=1)
        end_date = today
    elif periodo_opcao == "Mês Passado":
        first = today.replace(day=1) - pd.DateOffset(months=1)
        start_date = first
        end_date = first + pd.DateOffset(months=1) - pd.DateOffset(days=1)
    elif periodo_opcao == "Último Trimestre":
        start_date = today - pd.DateOffset(months=3)
        end_date = today
    elif periodo_opcao == "Este Ano":
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = df['Criado'].min().date() if not df.empty else today.date()
        end_date = df['Criado'].max().date() if not df.empty else today.date()
    
    if periodo_opcao == "Personalizado":
        date_range = st.date_input("Intervalo de Datas", [start_date, end_date])
        if len(date_range) == 2:
            start_date, end_date = date_range
    else:
        st.caption(f"De: {start_date.strftime('%d/%m/%Y')} Até: {end_date.strftime('%d/%m/%Y')}")

# 2. Filtros Hierárquicos (Cliente -> Projeto -> Módulo)
with st.sidebar.expander("🏢 Estrutura Organizacional", expanded=True):
    # Cliente
    clientes = sorted(df['Cliente'].unique()) if 'Cliente' in df.columns else ['Interno']
    sel_clientes = st.multiselect("Cliente", clientes, default=clientes)
    
    # Projeto (Filtrado por Cliente)
    df_l1 = df[df['Cliente'].isin(sel_clientes)] if 'Cliente' in df.columns else df
    projetos = sorted(df_l1['Projeto'].unique())
    sel_projetos = st.multiselect("Projetos", projetos, default=projetos)
    
    # Módulo (Filtrado por Projeto)
    df_l2 = df_l1[df_l1['Projeto'].isin(sel_projetos)]
    modulos = sorted(df_l2['Módulo'].unique()) if 'Módulo' in df_l2.columns else ['Geral']
    sel_modulos = st.multiselect("Módulo/Componente", modulos, default=modulos)

# 3. Filtros Operacionais
with st.sidebar.expander("⚙️ Filtros Operacionais", expanded=False):
    # Status
    status_options = sorted(df_l2['Status'].unique())
    sel_status = st.multiselect("Status", status_options, default=status_options)
    
    # Tipo
    tipos = sorted(df_l2['Tipo'].unique())
    sel_tipos = st.multiselect("Tipo de Tarefa", tipos, default=tipos)
    
    # Responsável
    responsaveis = sorted(df_l2['Responsável'].unique())
    sel_responsaveis = st.multiselect("Responsável", responsaveis, default=responsaveis)

# Aplicar Filtros ao Dataframe Principal (Com filtro de tempo)
mask_date = (df['Criado'].dt.date >= pd.to_datetime(start_date).date()) & (df['Criado'].dt.date <= pd.to_datetime(end_date).date())
mask_hierarchy = (
    (df['Projeto'].isin(sel_projetos)) &
    (df['Status'].isin(sel_status)) &
    (df['Tipo'].isin(sel_tipos)) &
    (df['Responsável'].isin(sel_responsaveis))
)

if 'Cliente' in df.columns:
    mask_hierarchy &= df['Cliente'].isin(sel_clientes)
if 'Módulo' in df.columns:
    mask_hierarchy &= df['Módulo'].isin(sel_modulos)

df_final = df[mask_date & mask_hierarchy]

# DataFrame Kanban (Sem filtro de tempo de criação, pois queremos ver o backlog atual completo)
df_kanban = df[mask_hierarchy]


# --- Dashboard Layout (Nova Estrutura Gerencial com Tailwind) ---
st.markdown(f"""
    <div class="flex justify-between items-center p-6 bg-white rounded-xl border border-gray-200 mb-8 shadow-sm">
        <div>
            <h1 class="m-0 text-3xl font-bold text-brand-blue">
                Relatório de Projetos
            </h1>
            <p class="m-0 text-gray-500 text-sm mt-1">Visão Integrada de Operações e Eficiência</p>
        </div>
        <div class="text-right border-l border-gray-300 pl-5">
            <div class="flex items-center justify-end gap-2 mb-1">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span class="text-sm font-semibold text-gray-700">Sistema Online</span>
            </div>
            <p class="m-0 text-gray-400 text-xs">Atualizado: {datetime.now().strftime('%H:%M')}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Tabs Structure ---
tabs = st.tabs([
    "📊 Visão Geral", 
    "📈 Indicadores (KPIs)", 
    "🏃 Painel Sprints", 
    "📋 Gestão Tarefas", 
    "👥 Visão Equipe",
    "⚠️ Análise Riscos",
    "📝 Dados Detalhados"
])

# --- TAB 1: VISÃO GERAL DOS PROJETOS ---
with tabs[0]:
    st.markdown("### 🏢 Visão Estratégica do Portfólio")
    
    # KPIs de Projetos
    total_projects = df_final['Projeto'].nunique()
    total_issues = len(df_final)
    
    # Projetos com atrasos (Issues vencidas e não concluídas)
    proj_atrasos = df_final[df_final['Atrasado'] == True]['Projeto'].nunique()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projetos Ativos", total_projects, f"{proj_atrasos} com atrasos", delta_color="inverse")
    c2.metric("Total de Issues", total_issues)
    c3.metric("Entregas no Prazo", f"{((1 - df_final['Atrasado'].mean()) * 100):.1f}%")
    
    # Velocity Geral (Story Points entregues por Mês)
    df_done = df_final[df_final['Status'].isin(status_concluidos)].copy()
    if not df_done.empty:
        df_done['Mes_Resolvido'] = df_done['Resolvido'].dt.to_period('M').astype(str)
        velocity = df_done.groupby('Mes_Resolvido')['Story Points'].sum().mean()
        c4.metric("Velocity Médio (SP/Mês)", f"{velocity:.1f}")
    else:
        c4.metric("Velocity Médio", "0")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Status Detalhado por Projeto")
        
        if not df_kanban.empty:
            # Color Map Monocromático (Tons de Azul - Clean & Corporate)
            color_map = {
                # Concluídos (Azul Escuro/Sólido)
                'Concluído': '#1E3A8A', 'Done': '#1E3A8A', 'Finalizado': '#1E3A8A', 'Resolvido': '#1E3A8A', 'Closed': '#1E3A8A',
                
                # Em Andamento (Azul Médio/Vibrante)
                'Em andamento': '#2563EB', 'In Progress': '#2563EB', 'Doing': '#2563EB',
                
                # Pendentes/Backlog (Azul Claro/Suave)
                'Tarefas pendentes': '#93C5FD', 'To Do': '#93C5FD', 'Backlog': '#BFDBFE', 'Open': '#BFDBFE',
                
                # Validação/QA (Azul Acinzentado)
                'Pronto para QA': '#64748B', 'Test': '#64748B', 'Teste Cury': '#64748B', 'Homologação': '#64748B',
                
                # Atenção/Crítico (Azul Noturno/Profundo - Mantendo a sobriedade)
                'Escalated': '#0F172A', 'ESCALADO': '#0F172A', 'Blocked': '#0F172A', 'Impedimento': '#0F172A',
                'Bug Report': '#172554', 'Bug': '#172554',
                
                # Cancelados/Outros (Cinza Azulado)
                'Cancelado': '#CBD5E1', 'Não procedente': '#CBD5E1', 'Não Procedente': '#CBD5E1', 
                'Análise': '#60A5FA', 'Aguardando': '#93C5FD', 'Conta': '#2563EB'
            }

            projs = sorted(df_kanban['Projeto'].unique())
            cols = st.columns(2)  # Grid de 2 colunas
            
            for i, proj in enumerate(projs):
                with cols[i % 2]:
                    # Filtrar dados do projeto (Usar df_kanban para ver TODO o backlog)
                    d_p = df_kanban[df_kanban['Projeto'] == proj]
                    
                    if d_p.empty:
                        continue

                    # Contagem por status
                    s_counts = d_p['Status'].value_counts().reset_index()
                    s_counts.columns = ['Status', 'Qtd']
                    
                    # Gráfico Individual
                    fig_p = px.bar(s_counts, x='Qtd', y='Status', orientation='h', 
                                   title=f"📁 {proj}", text_auto=True,
                                   color='Status', 
                                   color_discrete_map=color_map,
                                   color_discrete_sequence=px.colors.qualitative.Dark24)
                    
                    fig_p.update_layout(
                        template="plotly_white", 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)', 
                        font=dict(family="Inter"),
                        showlegend=False,
                        height=250,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para exibir.")

    with col2:
        st.subheader("📉 Burndown Acumulado (Portfólio)")
        # Burndown Simplificado (Criados vs Resolvidos acumulados no tempo)
        df_burn = df_final.copy()
        df_burn = df_burn.sort_values('Criado')
        df_burn['Criado_Count'] = 1
        df_burn['Acum_Criado'] = df_burn['Criado_Count'].cumsum()
        
        df_res_burn = df_final[df_final['Status'].isin(status_concluidos)].copy()
        df_res_burn = df_res_burn.sort_values('Resolvido')
        df_res_burn['Resolvido_Count'] = 1
        # Merge para alinhar no tempo
        timeline = pd.DataFrame({'Data': pd.concat([df_final['Criado'], df_final['Resolvido']]).unique()})
        timeline = timeline.sort_values('Data').dropna()
        
        # Aproximação visual
        fig_burn = go.Figure()
        fig_burn.add_trace(go.Scatter(x=df_burn['Criado'], y=df_burn['Acum_Criado'], mode='lines', name='Escopo Total', line=dict(color='#1E3A8A', width=3)))
        if not df_res_burn.empty:
             df_res_burn['Acum_Resolvido'] = range(1, len(df_res_burn) + 1)
             fig_burn.add_trace(go.Scatter(x=df_res_burn['Resolvido'], y=df_res_burn['Acum_Resolvido'], mode='lines', name='Entregue', fill='tozeroy', line=dict(color='#3B82F6')))
        
        fig_burn.update_layout(title="Curva de Entrega (Burnup)", template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_burn, use_container_width=True)

# --- TAB 2: INDICADORES CHAVE (KPIs) ---
with tabs[1]:
    st.markdown("### 🎯 Indicadores de Performance (KPIs)")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    
    # KPIs Corrigidos (Estoque vs Fluxo)
    # Abertas: Estoque Total (df_kanban)
    abertas = len(df_kanban[~df_kanban['Status'].isin(status_concluidos)])
    
    # Concluídas: Fluxo no Período (Resolvido dentro das datas selecionadas)
    if 'Resolvido' in df_kanban.columns:
        mask_res = (df_kanban['Resolvido'] >= pd.to_datetime(start_date)) & (df_kanban['Resolvido'] <= pd.to_datetime(end_date))
        concluidas = len(df_kanban[mask_res & df_kanban['Status'].isin(status_concluidos)])
    else:
        concluidas = 0
        
    # Críticos e Bugs: Estoque (df_kanban)
    criticos = len(df_kanban[df_kanban['Prioridade'].isin(['Highest', 'High', 'Critical']) & (~df_kanban['Status'].isin(status_concluidos))])
    bugs = len(df_kanban[df_kanban['Tipo'] == 'Bug']) # Total Geral
    bugs_pendentes = len(df_kanban[(df_kanban['Tipo'] == 'Bug') & (~df_kanban['Status'].isin(status_concluidos))])
    
    k1.metric("Issues Abertas (Backlog)", abertas)
    k2.metric("Concluídas (No Período)", concluidas)
    k3.metric("Bugs Pendentes", bugs_pendentes, f"{bugs} Total", delta_color="inverse")
    k4.metric("Itens Críticos", criticos, "Alta Prioridade", delta_color="inverse")
    
    if not df_done.empty:
        sla_medio = df_done['Lead Time'].mean()
        k5.metric("Lead Time Médio", f"{sla_medio:.1f} dias")
    else:
        k5.metric("Lead Time", "N/A")
        
    st.markdown("---")
    
    c_k1, c_k2 = st.columns(2)
    
    with c_k1:
        st.subheader("Distribuição por Tipo (Ativos)")
        # Usar df_kanban para ver distribuição do trabalho atual
        # Paleta monocromática azul para o Pie Chart
        blues_palette = ['#1E3A8A', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
        fig_type = px.pie(df_kanban, names='Tipo', hole=0.6, title="Volume por Tipo de Demanda (Backlog)", color_discrete_sequence=blues_palette)
        fig_type.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_type, use_container_width=True)
        
    with c_k2:
        st.subheader("Funil de Status")
        status_counts = df_kanban['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Qtd']
        # Funil em degradê de azul
        fig_funnel = px.funnel(status_counts, y='Status', x='Qtd', title="Funil de Execução Total", color='Qtd', color_discrete_sequence=['#1E3A8A'])
        fig_funnel.update_traces(marker=dict(color='#2563EB')) # Forçar azul corporativo
        fig_funnel.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_funnel, use_container_width=True)

# --- TAB 3: PAINEL DE SPRINTS ---
with tabs[2]:
    st.markdown("### 🏃 Gestão de Sprints")
    
    # Filtro de Sprints específico (Baseado em df_kanban para pegar todo histórico da sprint)
    all_sprints = sorted(df_kanban['Sprint'].unique())
    sprint_selection = st.multiselect("Filtrar Sprints", all_sprints, default=[s for s in all_sprints if s != 'Backlog'][:5])
    
    if not sprint_selection:
        st.info("Selecione sprints para visualizar.")
    else:
        df_sprint_view = df_kanban[df_kanban['Sprint'].isin(sprint_selection)]
        
        # Métricas da Sprint
        sp_total = df_sprint_view['Story Points'].sum()
        sp_done = df_sprint_view[df_sprint_view['Status'].isin(status_concluidos)]['Story Points'].sum()
        progress_sprint = (sp_done / sp_total * 100) if sp_total > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Story Points Totais", f"{sp_total:.0f}")
        m2.metric("Story Points Entregues", f"{sp_done:.0f}")
        m3.metric("Progresso Geral", f"{progress_sprint:.1f}%")
        
        # Gráfico de Barras por Sprint
        fig_sprint_bar = px.bar(df_sprint_view.groupby(['Sprint', 'Status']).sum(numeric_only=True).reset_index(), 
                                x='Sprint', y='Story Points', color='Status', title="Story Points por Sprint e Status", barmode='group',
                                color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sprint_bar.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_sprint_bar, use_container_width=True)

# --- TAB 4: GESTÃO DE TAREFAS ---
with tabs[3]:
    st.markdown("### 📋 Gestão Operacional de Tarefas")
    
    # Kanban Board View (Simplificado em colunas Streamlit)
    st.subheader("📌 Quadro Kanban Resumido")
    
    # Definindo colunas padrão (Adaptar conforme seus status reais)
    cols_kanban = st.columns(4)
    kanban_mapping = {
        'To Do': ['To Do', 'Backlog', 'Open', 'New'],
        'In Progress': ['In Progress', 'Em Andamento', 'Development', 'Review'],
        'Testing': ['Testing', 'QA', 'Homologation', 'In Review'],
        'Done': status_concluidos
    }
    
    kanban_titles = ['A Fazer', 'Em Progresso', 'Testes/Review', 'Concluído']
    
    for idx, (group_name, statuses) in enumerate(kanban_mapping.items()):
        with cols_kanban[idx]:
            st.markdown(f"**{kanban_titles[idx]}**")
            items = df_kanban[df_kanban['Status'].isin(statuses)].head(10)
            for _, item in items.iterrows():
                priority_color = "🔴" if item['Prioridade'] in ['High', 'Highest', 'Critical'] else "🔵"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #555;">
                    <small style="color: #aaa;">{item['Chave']} | {item['Responsável']}</small><br>
                    {priority_color} {item['Resumo'][:50]}...
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Issues Antigas
    st.subheader("🐢 Tarefas Estagnadas (Top 10 Mais Antigas Abertas)")
    oldest = df_kanban[~df_kanban['Status'].isin(status_concluidos)].sort_values('Criado').head(10)
    if not oldest.empty:
        # Calcular idade em dias
        oldest['Dias Aberto'] = (datetime.now() - oldest['Criado']).dt.days
        st.dataframe(oldest[['Chave', 'Resumo', 'Responsável', 'Status', 'Criado', 'Dias Aberto']], use_container_width=True)
    else:
        st.success("Nenhuma tarefa antiga encontrada!")

# --- TAB 5: VISÃO DE EQUIPE ---
with tabs[4]:
    st.markdown("### 👥 Performance & Carga da Equipe")
    
    # Workload
    st.subheader("Carga de Trabalho (Issues Ativas)")
    df_team_active = df_kanban[~df_kanban['Status'].isin(status_concluidos)]
    
    if not df_team_active.empty:
        team_load = df_team_active.groupby('Responsável').agg({'Chave': 'count', 'Story Points': 'sum'}).reset_index()
        team_load.columns = ['Responsável', 'Qtd Issues', 'Story Points']
        team_load = team_load.sort_values('Story Points', ascending=True)
        
        fig_team = px.bar(team_load, y='Responsável', x=['Qtd Issues', 'Story Points'], orientation='h', 
                          title="Carga por Membro", barmode='group',
                          color_discrete_sequence=['#00f3ff', '#bc13fe'])
        fig_team.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_team, use_container_width=True)
        
        # Alerta de Burnout (Ex: > 10 issues ou > 20 points - Ajustável)
        overloaded = team_load[(team_load['Qtd Issues'] > 10) | (team_load['Story Points'] > 20)]
        if not overloaded.empty:
            st.warning(f"⚠️ Alerta de Sobrecarga: {', '.join(overloaded['Responsável'].tolist())}")
    else:
        st.info("Equipe sem itens ativos.")

# --- TAB 6: RISCOS ---
with tabs[5]:
    st.markdown("### ⚠️ Matriz de Riscos & Atrasos")
    
    r1, r2 = st.columns(2)
    
    with r1:
        st.subheader("🔥 Heatmap de Riscos (Atrasos por Módulo/Status)")
        if 'Módulo' in df_final.columns and not df_final.empty:
            df_atrasos = df_final[df_final['Atrasado'] == True]
            if not df_atrasos.empty:
                heatmap_data = df_atrasos.groupby(['Módulo', 'Status']).size().reset_index(name='Qtd')
                fig_heat = px.density_heatmap(heatmap_data, x='Status', y='Módulo', z='Qtd', title="Concentração de Atrasos", color_continuous_scale='Magma')
                fig_heat.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.success("Sem itens atrasados para gerar heatmap.")
    
    with r2:
        st.subheader("🚨 Lista de Prioridade Crítica")
        critical_issues = df_kanban[
            (
                (df_kanban['Prioridade'].isin(['Highest', 'Critical', 'High'])) |
                (df_kanban['Status'].isin(['Escalated', 'Blocked', 'Impediment']))
            ) & 
            (~df_kanban['Status'].isin(status_concluidos))
        ]
        if not critical_issues.empty:
            st.dataframe(critical_issues[['Chave', 'Resumo', 'Responsável', 'Status', 'Prioridade']], use_container_width=True)
        else:
            st.success("Nenhum item crítico pendente.")

    st.markdown("---")
    st.subheader("📊 Projetos com Maior Volume de Atrasos")
    if 'Atrasado' in df_final.columns:
        df_risk_proj = df_final[df_final['Atrasado'] == True].groupby('Projeto').size().reset_index(name='Qtd Atrasos')
        if not df_risk_proj.empty:
            df_risk_proj = df_risk_proj.sort_values('Qtd Atrasos', ascending=False).head(10)
            
            fig_risk_proj = px.bar(df_risk_proj, x='Qtd Atrasos', y='Projeto', orientation='h', 
                                   title="Top 10 Projetos com Atrasos", text='Qtd Atrasos', color='Qtd Atrasos', color_continuous_scale='Reds')
            fig_risk_proj.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
            st.plotly_chart(fig_risk_proj, use_container_width=True)
        else:
            st.info("Nenhum projeto com atrasos registrados.")

# --- TAB 7: DETALHES ---
with tabs[6]:
    st.markdown("### 📝 Base de Dados Completa")
    
    # Export Buttons
    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 3])
    
    with col_exp1:
        # Excel Export
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Dados')
        processed_data = output.getvalue()
        
        st.download_button(
            label="📥 Exportar Excel",
            data=processed_data,
            file_name=f"jira_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with col_exp2:
        # PDF Export
        def create_pdf(dataframe):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            def clean_text(text):
                return str(text).encode('latin-1', 'replace').decode('latin-1')
            
            # Title
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(200, 10, txt=clean_text("Relatório de Projetos - Jira Nexus"), ln=True, align='C')
            pdf.ln(10)
            
            # Timestamp
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=clean_text(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"), ln=True, align='C')
            pdf.ln(10)
            
            # Summary Metrics
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=clean_text("Resumo Executivo"), ln=True, align='L')
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, txt=clean_text(f"Total de Tickets Filtrados: {len(dataframe)}"), ln=True)
            pdf.cell(0, 10, txt=clean_text(f"Projetos Ativos: {dataframe['Projeto'].nunique() if 'Projeto' in dataframe.columns else 0}"), ln=True)
            pdf.ln(10)
            
            # Table Header
            pdf.set_font("Arial", style="B", size=10)
            pdf.cell(30, 10, clean_text("Chave"), 1)
            pdf.cell(40, 10, clean_text("Status"), 1)
            pdf.cell(60, 10, clean_text("Responsável"), 1)
            pdf.cell(50, 10, clean_text("Projeto"), 1)
            pdf.ln()
            
            # Table Rows (Limit 50)
            pdf.set_font("Arial", size=8)
            for i, row in dataframe.head(50).iterrows():
                pdf.cell(30, 10, clean_text(str(row.get('Chave', ''))[:15]), 1)
                pdf.cell(40, 10, clean_text(str(row.get('Status', ''))[:20]), 1)
                pdf.cell(60, 10, clean_text(str(row.get('Responsável', ''))[:30]), 1)
                pdf.cell(50, 10, clean_text(str(row.get('Projeto', ''))[:25]), 1)
                pdf.ln()
            
            if len(dataframe) > 50:
                pdf.cell(0, 10, txt=clean_text(f"... e mais {len(dataframe) - 50} itens (exporte Excel para ver tudo)"), ln=True)
                
            return pdf.output(dest='S').encode('latin-1')

        try:
            pdf_data = create_pdf(df_final)
            st.download_button(
                label="📄 Exportar PDF",
                data=pdf_data,
                file_name=f"jira_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
        
    st.dataframe(df_final, width=None, use_container_width=True)

