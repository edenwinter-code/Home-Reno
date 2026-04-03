import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
# Replace with the exact name of your Google Sheet
SPREADSHEET_NAME = "1OKXpUghhzU-3eT0jx8fSYcrASLr4TkjfjnT3ep3TT_Q" 

# --- 2. AUTHENTICATION FUNCTION ---
def get_gspread_client():
    """Authenticates and returns a gspread client using Streamlit secrets."""
    # These scopes are required to talk to Google Sheets and Drive
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # This pulls the credentials from the [gcp_service_account] block in your Secrets
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["service_account"], 
            scopes=scopes
        )
        return gspread.authorize(creds)
    except KeyError:
        st.error("Error: 'gcp_service_account' not found in Streamlit Secrets.")
        st.stop()
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        st.stop()

# --- 3. DATA LOADING FUNCTION ---
@st.cache_data(ttl=600) # Optional: Caches data for 10 minutes to speed up the app
def load_data(sheet_name):
    """Connects to a specific worksheet and returns the data as a DataFrame."""
    try:
        client = get_gspread_client()
        # Open the spreadsheet by name
        sh = client.open(SPREADSHEET_NAME)
        # Select the worksheet (e.g., "Budget")
        worksheet = sh.worksheet(sheet_name)
        # Convert the data into a Pandas DataFrame
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Spreadsheet '{SPREADSHEET_NAME}' not found. Check the name and sharing permissions.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 4. MAIN APP LOGIC ---
st.title("Home Reno Dashboard")

# Call the function for your "Budget" sheet
budget_df = load_data("Budget")

if not budget_df.empty:
    st.subheader("Budget Data")
    st.write(budget_df)
else:
    st.info("No data found in the 'Budget' worksheet.")

# 5. Save Button
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
