import streamlit as st
from jira import JIRA
import pandas as pd
import toml

# Load secrets directly since we are running a standalone script
secrets = toml.load(".streamlit/secrets.toml")

def get_jira_counts():
    try:
        jira = JIRA(server=secrets["jira"]["url"], basic_auth=(secrets["jira"]["username"], secrets["jira"]["token"]))
        
        # Search for all issues in relevant projects (or all projects)
        jql = 'created >= -730d OR statusCategory != Done' 
        print(f"Executing JQL: {jql}")
        
        # Try fetching ALL issues using maxResults=0
        issues = jira.search_issues(jql, maxResults=0, fields="status,summary,project")
        
        print(f"Total issues fetched: {len(issues)}")
        
        # Count by Project and Status
        project_status_counts = {}
        for issue in issues:
            proj_name = issue.fields.project.name
            status = issue.fields.status.name
            
            if proj_name not in project_status_counts:
                project_status_counts[proj_name] = {}
            
            project_status_counts[proj_name][status] = project_status_counts[proj_name].get(status, 0) + 1
            
        print("\n--- Status Counts per Project from API ---")
        for proj, counts in project_status_counts.items():
            print(f"\nProject: {proj}")
            for status, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {status}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_jira_counts()
