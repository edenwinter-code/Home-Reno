import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
# Put your ID here once so the whole app can use it
SPREADSHEET_ID = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q"

# --- 2. AUTHENTICATION FUNCTION ---
def get_gspread_client():
    """Authenticates and returns a gspread client using Streamlit secrets."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Note: Using "service_account" as the key to match your secrets
        creds = Credentials.from_service_account_info(
            st.secrets["service_account"], 
            scopes=scopes
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        st.stop()

# --- 3. DATA LOADING FUNCTION ---
@st.cache_data(ttl=600)
def load_data(sheet_name):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        # Switch to get_all_values for better reliability
        data = worksheet.get_all_values()
        
        if not data:
            return pd.DataFrame()
            
        # Manually create the DataFrame: 
        # Row 0 becomes headers, everything else becomes the data
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
        
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 4. MAIN APP LOGIC ---
st.title("Home Reno Dashboard")

# Load the Budget data
budget_df = load_data("Budget")

if not budget_df.empty:
    st.subheader("Budget Data")
    # Using data_editor so you can actually change the numbers
    edited_budget = st.data_editor(budget_df) 
else:
    st.info("No data found in the 'Budget' worksheet.")

# --- 5. SAVE BUTTON ---
st.divider()
if st.button("💾 Save All Changes"):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # Save Budget
        b_sheet = sh.worksheet("Budget")
        # Overwrite the sheet with the edited data
        b_sheet.update([edited_budget.columns.values.tolist()] + edited_budget.values.tolist())
        
        st.success("All data successfully synced to the cloud!")
        st.cache_data.clear() # Clear cache so it shows the new data on refresh
    except Exception as e:
        st.error(f"Failed to save: {e}")
    
    st.success("All data successfully synced to the cloud!")
