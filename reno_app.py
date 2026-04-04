import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
SPREADSHEET_ID = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q"

# --- 2. AUTHENTICATION ---
def get_gspread_client():
    # CORRECT SCOPES for Google Sheets and Google Drive API
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Matches the [service_account] label in your Streamlit Secrets
        creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        st.stop()

# --- 3. DATA LOADING ---
@st.cache_data(ttl=600)
def load_data(sheet_name):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        # Use get_all_values (more reliable than get_all_records)
        data = worksheet.get_all_values()
        
        if not data or len(data) < 1:
            return pd.DataFrame()
            
        # If there's only a header row, create an empty DF with those headers
        if len(data) == 1:
            return pd.DataFrame(columns=data[0])
            
        # Standard case: row 0 is headers, data is the rest
        return pd.DataFrame(data[1:], columns=data[0])
        
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 4. MAIN APP ---
st.title("Home Reno Dashboard")

budget_df = load_data("Budget")

# Check if we have at least columns (even if 0 rows of data)
if not budget_df.columns.empty:
    st.subheader("Budget Tracking")
    # Using data_editor so you can add/edit rows
    edited_budget = st.data_editor(budget_df, num_rows="dynamic", key="budget_editor")
else:
    st.warning("Could not find headers in the 'Budget' tab. Check your Google Sheet.")

# --- 5. SAVE CHANGES ---
st.divider()
if st.button("💾 Save All Changes"):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # Save Budget Tab
        b_sheet = sh.worksheet("Budget")
        b_sheet.clear()
        # Convert DataFrame back to Google Sheets format (Headers + Rows)
        data_to_save = [edited_budget.columns.values.tolist()] + edited_budget.values.tolist()
        b_sheet.update(data_to_save)
        
        st.success("Successfully synced to Google Sheets!")
        st.cache_data.clear() # Force app to see new data
    except Exception as e:
        st.error(f"Save failed: {e}")
