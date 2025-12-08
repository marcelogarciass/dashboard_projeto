import streamlit as st
from jira import JIRA
import pandas as pd
import toml

# Load secrets directly since we are running a standalone script
secrets = toml.load(".streamlit/secrets.toml")

def get_jira_counts():
    try:
        jira = JIRA(server=secrets["jira"]["url"], basic_auth=(secrets["jira"]["username"], secrets["jira"]["token"]))
        
        projects = jira.projects()
        target_project = None
        for p in projects:
            if "Manutenção" in p.name:
                target_project = p
                print(f"Found Project: {p.name} (Key: {p.key})")
                break
        
        if not target_project:
            print("Project 'Manutenção de Projetos' not found via API list.")
            return

        # Explicitly set a large maxResults to bypass default 50 limit
        jql = f'project = "{target_project.key}"'
        print(f"Executing JQL: {jql}")
        
        # Try fetching ALL issues using maxResults=0
        issues = jira.search_issues(jql, maxResults=0, fields="status,summary")
        
        print(f"Total issues fetched: {len(issues)}")
        
        # Count by Status
        status_counts = {}
        for issue in issues:
            status = issue.fields.status.name
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print("\n--- Status Counts from API ---")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{status}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_jira_counts()
