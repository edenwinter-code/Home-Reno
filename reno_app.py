import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
# Replace with your actual spreadsheet ID
SPREADSHEET_ID = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q" 

st.set_page_config(page_title="Reno Manager", layout="wide")

# --- AUTHENTICATION ---
@st.cache_resource
def get_gspread_client():
    # Load credentials from secrets
    creds_dict = st.secrets["connections"]["gsheets"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- DATA HANDLING ---
def load_data(worksheet_name):
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(worksheet_name)
    return pd.DataFrame(worksheet.get_all_records())

st.title("🏗️ Professional Reno Manager")

# Budget
st.header("Financial Overview")
budget_df = load_data("Budget")
edited_budget = st.data_editor(budget_df, num_rows="dynamic")

# Timeline
st.header("Project Timeline")
timeline_df = load_data("Timeline")
edited_timeline = st.data_editor(timeline_df, num_rows="dynamic")

# Save Button
if st.button("💾 Save Changes"):
    # This example updates the first worksheet as a demonstration
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Budget")
    sheet.update([edited_budget.columns.values.tolist()] + edited_budget.values.tolist())
    st.success("Data updated!")
