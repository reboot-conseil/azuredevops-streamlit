import math
import streamlit as st
import base64
import datetime

from azure.devops.connection import Connection
from azure.devops.v7_1.git import GitPullRequestSearchCriteria
from msrest.authentication import BasicAuthentication

st.set_page_config(page_title = "Azure DevOps Activies")#, layout = "wide")

personal_access_token = 'xxx'
organization_url = 'https://dev.azure.com/xxx'
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

core_client = connection.clients.get_core_client()
git_client = connection.clients.get_git_client()
graph_client = connection.clients.get_graph_client()

# Get and sort projects and prs
projects = core_client.get_projects(get_default_team_image_url = True)
data = []
for project in projects:
   prs = git_client.get_pull_requests_by_project(project.id, GitPullRequestSearchCriteria(status = "All"))
   data.append({ "project": project, "prs": prs })
data = sorted(data, key = lambda x: x["prs"][0].creation_date.timestamp() if len(x["prs"]) > 0 else 0, reverse = True)

imgs = {}
for d in data:
   project = d["project"]
   col1, col2 = st.columns([0.1, 0.9], gap = "large")
   #st.write(project)
   with col1:
      st.image(project.default_team_image_url, width = 50)
   with col2:
      st.subheader(project.name, anchor = False)
   prs = d["prs"]
   for pr in prs[:5]:
      col1, col2, col3, col4, col5 = st.columns([0.45, 0.14, 0.14, 0.04, 0.23])
      with col1:
         st.write(f"[\#{pr.code_review_id} - {pr.title}]({pr.url})")
      with col2:
         st.write(pr.creation_date.strftime("%d %b %Y"))
      with col3:
         if pr.status == "active":
            st.write("🔔 **Active** 🔔")
         else:
            st.write(pr.status.title())
         #st.write(pr.status.title() + (" - " + pr.closed_date.strftime("%d %b %Y") if pr.closed_date is not None else "" ))
      with col4:
         if imgs.get(pr.created_by.descriptor) is None:
            res = graph_client.get_avatar(pr.created_by.descriptor)
            imgs[pr.created_by.descriptor] = base64.b64decode(res.value)
         st.image(imgs[pr.created_by.descriptor], width = 25)
      with col5:
         st.write(pr.created_by.display_name)
      #st.write(pr)
   st.divider()