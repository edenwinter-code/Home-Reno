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

# --- 4. MAIN APP ---
st.title("Home Reno Dashboard")

# A. BUDGET SECTION
st.header("💰 Budget Tracking")
budget_df = load_data("Budget")
if not budget_df.columns.empty:
    edited_budget = st.data_editor(budget_df, num_rows="dynamic", key="budget_editor")
else:
    st.warning("Check 'Budget' tab in Sheets.")

# B. TIMELINE SECTION (NEW)
st.divider()
st.header("📅 Project Timeline")

# 1. Load Data (or use default if sheet is empty)
timeline_df = load_data("Timeline")

if timeline_df.empty:
    # Default fallback data if Google Sheet is empty
    default_data = [
        {"Task": "Planning", "Start": "2026-04-01", "Finish": "2026-05-15", "Resource": "Owner"},
        {"Task": "Demolition", "Start": "2026-05-16", "Finish": "2026-05-25", "Resource": "Contractor"},
    ]
    timeline_df = pd.DataFrame(default_data)

# 2. Edit Data
edited_timeline = st.data_editor(timeline_df, num_rows="dynamic", key="timeline_editor")

# 3. Render Gantt Chart
# Plotly needs real DateTime objects, not strings
if not edited_timeline.empty:
    try:
        # Create a copy for plotting so we don't break the string format for saving
        plot_df = edited_timeline.copy()
        plot_df["Start"] = pd.to_datetime(plot_df["Start"])
        plot_df["Finish"] = pd.to_datetime(plot_df["Finish"])

        fig = px.timeline(
            plot_df, 
            x_start="Start", 
            x_end="Finish", 
            y="Task", 
            color="Resource",
            title="Construction Schedule"
        )
        fig.update_yaxes(autorange="reversed") # Lists tasks top-to-bottom
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Chart Error: Ensure dates are YYYY-MM-DD. ({e})")

# --- 5. SAVE CHANGES (UPDATED) ---
st.divider()
if st.button("💾 Save All Changes"):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # 1. Save Budget
        b_sheet = sh.worksheet("Budget")
        b_sheet.clear()
        b_sheet.update([edited_budget.columns.values.tolist()] + edited_budget.values.tolist())

        # 2. Save Timeline
        # Note: You must create a tab named "Timeline" in your Google Sheet first!
        t_sheet = sh.worksheet("Timeline")
        t_sheet.clear()
        t_sheet.update([edited_timeline.columns.values.tolist()] + edited_timeline.values.tolist())
        
        st.success("Successfully synced Budget & Timeline to Google Sheets!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Save failed: {e}")
