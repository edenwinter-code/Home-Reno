import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
SPREADSHEET_ID = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q"

st.set_page_config(page_title="Reno Manager", layout="wide")

# --- AUTHENTICATION ---
@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    scopes = ["https://googleapis.com", "https://googleapis.com"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

# --- DATA HANDLING ---
def load_data(worksheet_name):
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    
    # If the sheet is empty, return a starter table so it's editable
    if not data:
        if worksheet_name == "Budget":
            return pd.DataFrame({"Category": ["Structural"], "Estimated": [0], "Actual": [0]})
        else:
            return pd.DataFrame({"Task": ["Planning"], "Start": ["2026-04-01"], "Finish": ["2026-04-15"], "Resource": ["Owner"]})
    return pd.DataFrame(data)

st.title("🏗️ Professional Reno Manager")

# 1. Budget Section
st.header("Financial Overview")
budget_df = load_data("Budget")
# CRITICAL: We added key="budget_table"
edited_budget = st.data_editor(budget_df, num_rows="dynamic", key="budget_table")

# 2. Timeline Section
st.header("Project Timeline")
timeline_df = load_data("Timeline")
# CRITICAL: We added key="timeline_table"
edited_timeline = st.data_editor(timeline_df, num_rows="dynamic", key="timeline_table")

# 3. Save Button
st.divider()
if st.button("💾 Save All Changes"):
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    
    # Save Budget
    b_sheet = sh.worksheet("Budget")
    b_sheet.clear() # Clear old data
    b_sheet.update([edited_budget.columns.values.tolist()] + edited_budget.values.tolist())
    
    # Save Timeline
    t_sheet = sh.worksheet("Timeline")
    t_sheet.clear()
    t_sheet.update([edited_timeline.columns.values.tolist()] + edited_timeline.values.tolist())
    
    st.success("All data successfully synced to the cloud!")
