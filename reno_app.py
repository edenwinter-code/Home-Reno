import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

URL = https://docs.google.com/spreadsheets/d/14j8yI42-0bmqydQCNjMvSXJr1TweapUCUvtRiXvp41I/edit?usp=sharing
conn = st.connection("gsheets", type=GSheetsConnection)

default_budget = {"Category": ["Structural", "Kitchen"], "Estimated": [0, 0], "Actual": [0, 0]}
default_timeline = [dict(Task="Planning", Start='2026-04-01', Finish='2026-04-15', Resource="Owner")]

if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(spreadsheet=url, worksheet="Budget")
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=url, worksheet="Timeline")

st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")


# 1. Budget Tracker
st.header("Financial Overview")
edited_budget = st.data_editor(st.session_state.budget_df, num_rows="dynamic", key="b_edit")
default_budget = {
    "Category": ["Structural", "Kitchen", "Electrical", "Flooring", "Painting"],
    "Estimated": [10000, 15000, 5000, 8000, 3000],
    "Actual": [11500, 0, 4800, 0, 0]
}
df_budget = load_data("budget.csv", default_budget)
df_budget = pd.DataFrame(default_budget)
df_budget["Difference"] = df_budget["Estimated"] - df_budget["Actual"]
df_budget = edited_budget 

# 2. Project Timeline (Gantt Chart)
st.header("Project Timeline")
edited_timeline = st.data_editor(st.session_state.timeline_df, num_rows="dynamic", key="t_edit")
default_timeline = [
    dict(Task="Planning & Permits", Start='2026-04-01', Finish='2026-05-15', Resource="Owner"),
    dict(Task="Demolition", Start='2026-05-16', Finish='2026-05-25', Resource="Contractor"),
    dict(Task="Structural Work", Start='2026-05-26', Finish='2026-06-20', Resource="Builder"),
]
df_timeline = load_data("timeline.csv", default_timeline)
df_timeline = pd.DataFrame(default_timeline)
fig = px.timeline(edited_timeline, x_start="Start", x_end="Finish", y="Task", color="Resource")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 3. Document Upload
st.header("Permits & Contracts")
uploaded_file = st.file_uploader("Upload site photos or PDF contracts")
if uploaded_file:
    st.success(f"Saved: {uploaded_file.name}")

# 4. Save Button
st.divider()
if st.button("☁️ Save to Cloud"):
    conn.update(spreadsheet=url, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=url, worksheet="Timeline", data=edited_timeline)
    st.success("Saved to Google Sheets! Access it anywhere now.")