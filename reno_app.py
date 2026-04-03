import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Page Config MUST be first
st.set_page_config(page_title="My Home Reno Planner", layout="wide")

# 2. Define the URL (Notice it is lowercase now to match the rest of the code)
url = "https://docs.google.com/spreadsheets/d/14j8yI42-0bmqydQCNjMvSXJr1TweapUCUvtRiXvp41I/edit?gid=362451620#gid=362451620"

st.title("🏗️ Cloud Reno Manager")

# 3. Create Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. Load Data from Cloud (Using st.session_state to remember changes)
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(spreadsheet=url, worksheet="Budget")
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=url, worksheet="Timeline")

# 5. Budget Tracker Section
st.header("Financial Overview")
edited_budget = st.data_editor(st.session_state.budget_df, num_rows="dynamic", key="b_edit")

# 6. Timeline Section
st.header("Project Timeline")
edited_timeline = st.data_editor(st.session_state.timeline_df, num_rows="dynamic", key="t_edit")

# Draw the Chart
fig = px.timeline(edited_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 7. Save Button
st.divider()
if st.button("☁️ Save to Cloud"):
    # This pushes your edits to Google Sheets
    conn.update(spreadsheet=url, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=url, worksheet="Timeline", data=edited_timeline)
    
    # This updates the app's memory so it doesn't "revert" on refresh
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.success("Saved to Google Sheets! Access it anywhere now.")
