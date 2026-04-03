import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Page Config MUST be first
st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")

# 2. Define the URL (Must be ABOVE the conn.read lines)
SHEET_URL = "https://google.com"

# 3. Create Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. Load Data from Cloud
if 'budget_df' not in st.session_state:
    # We use SHEET_URL here, which we defined above in Step 2
    st.session_state.budget_df = conn.read(spreadsheet=SHEET_URL, worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=SHEET_URL, worksheet="Timeline", ttl=0)

# 5. Display Budget Table
st.header("Financial Overview")
edited_budget = st.data_editor(st.session_state.budget_df, num_rows="dynamic", key="b_edit")

# 6. Display Timeline & Chart
st.header("Project Timeline")
edited_timeline = st.data_editor(st.session_state.timeline_df, num_rows="dynamic", key="t_edit")

fig = px.timeline(edited_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 7. Save Button
st.divider()
if st.button("☁️ Save All Changes to Cloud"):
    conn.update(spreadsheet=SHEET_URL, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=SHEET_URL, worksheet="Timeline", data=edited_timeline)
    
    # Update memory so it doesn't "revert"
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.success("Successfully saved to Google Sheets!")
