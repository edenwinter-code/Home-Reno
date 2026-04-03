import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")

# The connection now automatically looks in 'Secrets' for the key!
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data using the secure connection
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(worksheet="Timeline", ttl=0)

# Display Budget
st.header("Financial Overview")
edited_budget = st.data_editor(st.session_state.budget_df, num_rows="dynamic", key="b_edit")

# Display Timeline & Chart
st.header("Project Timeline")
edited_timeline = st.data_editor(st.session_state.timeline_df, num_rows="dynamic", key="t_edit")

fig = px.timeline(edited_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# Save Button
if st.button("☁️ Save to Cloud"):
    conn.update(worksheet="Budget", data=edited_budget)
    conn.update(worksheet="Timeline", data=edited_timeline)
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.success("Successfully saved to Google Sheets via Secure Key!")
