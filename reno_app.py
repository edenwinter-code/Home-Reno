import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")

# 1. THE ID METHOD (Much safer than the full URL)
# This is just the ID part of your link
SHEET_ID = "14j8yI42-0bmqydQCNjMvSXJr1TweapUCUvtRiXvp41I"
# We re-construct the URL perfectly here
full_url = f"https://google.com{SHEET_ID}/edit"

# 2. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Load Data - We use 'spreadsheet=full_url' explicitly
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(spreadsheet=full_url, worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=full_url, worksheet="Timeline", ttl=0)

# 4. Display
st.header("Financial Overview")
edited_budget = st.data_editor(st.session_state.budget_df, num_rows="dynamic", key="b_edit")

st.header("Project Timeline")
edited_timeline = st.data_editor(st.session_state.timeline_df, num_rows="dynamic", key="t_edit")

# 5. Chart
fig = px.timeline(edited_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 6. Save Button - Use 'spreadsheet=full_url' here too!
if st.button("☁️ Save to Cloud"):
    conn.update(spreadsheet=full_url, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=full_url, worksheet="Timeline", data=edited_timeline)
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.success("Saved to Google Sheets!")
