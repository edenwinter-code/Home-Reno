import streamlit as st
import gspread
import pandas as pd
import plotly.express as px  # <--- REQUIRED NEW IMPORT
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION & AUTH (Keep your existing code here) ---
SPREADSHEET_ID = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q"

def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # ... (Keep your existing auth try/except block) ...
    # Placeholder for brevity; assume your existing auth code is here
    creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def load_data(sheet_name):
    # ... (Keep your existing load_data function) ...
    # Placeholder for brevity; assume your existing load_data code is here
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_values()
    if not data or len(data) < 1: return pd.DataFrame()
    if len(data) == 1: return pd.DataFrame(columns=data[0])
    return pd.DataFrame(data[1:], columns=data[0])

st.title("🏗️ Cloud Reno Manager")

# 3. Load Data (Added Todo Worksheet)
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(worksheet="Timeline", ttl=0)
if 'todo_df' not in st.session_state:
    # Ensure your Google Sheet has a worksheet named "Todo" 
    # with columns: Done (TRUE/FALSE), Task, and Notes
    st.session_state.todo_df = conn.read(worksheet="Todo", ttl=0)

# 4. Todo List Section (New)
st.header("✅ Project Todo List")
edited_todo = st.data_editor(
    st.session_state.todo_df, 
    num_rows="dynamic", 
    key="todo_edit",
    use_container_width=True
)

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
    conn.update(worksheet="Budget", data=edited_budget)
    conn.update(worksheet="Timeline", data=edited_timeline)
    conn.update(worksheet="Todo", data=edited_todo) # Save the new list
    
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.session_state.todo_df = edited_todo
    st.success("All data saved to Google Sheets!")
