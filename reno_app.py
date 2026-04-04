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

# --- C. TODO LIST SECTION (NEW) ---
st.divider()
st.header("✅ Project Todo List")

# 1. Load Todo Data
todo_df = load_data("Todo")

# 2. Display Todo Editor
# This uses CheckboxColumn for the 'Done' field
edited_todo = st.data_editor(
    todo_df,
    num_rows="dynamic",
    key="todo_editor",
    use_container_width=True,
    column_config={
        "Done": st.column_config.CheckboxColumn(
            "Done",
            help="Check off completed tasks",
            default=False,
        ),
        "Task": st.column_config.TextColumn("Task", width="medium"),
        "Notes": st.column_config.TextColumn("Notes", width="large"),
    }
)

# --- SIDEBAR: QUICK CALCULATORS (Section 2) ---
with st.sidebar:
    st.header("🧮 Material Calculators")
    calc_type = st.selectbox("Choose Calculator", ["Tile/Flooring", "Paint"])
    
    if calc_type == "Tile/Flooring":
        length = st.number_input("Length (m)", min_value=0.0, value=10.0)
        width = st.number_input("Width (m)", min_value=0.0, value=10.0)
        waste = st.slider("Waste Allowance (%)", 0, 20, 10)
        area = length * width
        total = area * (1 + waste/100)
        st.metric("Total Sq m Needed", m"{total:.1m} sq m")
        
    elif calc_type == "Paint":
        p_length = st.number_input("Wall Length (ft)", min_value=0.0, value=12.0)
        p_height = st.number_input("Wall Height (ft)", min_value=0.0, value=8.0)
        coats = st.number_input("Number of Coats", 1, 3, 2)
        # Avg coverage: 350 sq ft per gallon
        gallons = ((p_length * p_height) * coats) / 350
        st.metric("Gallons Needed", f"{gallons:.2f}")

# --- D. CONTACTS DIRECTORY (Section 3) ---
st.divider()
st.header("📞 Trades & Contacts")
contacts_df = load_data("Contacts")
edited_contacts = st.data_editor(contacts_df, num_rows="dynamic", key="contact_edit", use_container_width=True)

# --- E. SHOPPING WISHLIST (Section 4) ---
st.divider()
st.header("🛒 Shopping Wishlist")
wishlist_df = load_data("Wishlist")
edited_wishlist = st.data_editor(
    wishlist_df, 
    num_rows="dynamic", 
    key="wish_edit",
    column_config={
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "Link": st.column_config.LinkColumn("Product Link")
    },
    use_container_width=True
)
# Calculate and display the total
if not edited_wishlist.empty:
    # Clean the Price column to ensure it's numeric before summing
    wishlist_total = pd.to_numeric(edited_wishlist["Price"], errors='coerce').fillna(0).sum()
    
    st.markdown(f"### 🛒 Wishlist Total: **${wishlist_total:,.2f}**")
    
    # Optional: Compare it to your remaining budget
    # total_diff is calculated in your Budget section
    if 'total_diff' in locals():
        if wishlist_total > total_diff:
            st.warning(f"⚠️ This is ${wishlist_total - total_diff:,.2f} over your remaining budget!")
        else:
            st.success(f"✅ You have enough remaining budget to cover this wishlist.")

# --- A. BUDGET SECTION (UPDATED) ---
st.header("💰 Budget Tracking")
budget_df = load_data("Budget")

if not budget_df.columns.empty:
    # 1. CLEANING: Convert Google Sheets text ("$1,000") to Numbers (1000.0)
    # This regex removes '$' and ',' before converting to float
    cols_to_clean = ["Estimated", "Actual"]
    
    for col in cols_to_clean:
        if col in budget_df.columns:
            budget_df[col] = (
                budget_df[col]
                .astype(str)                     # Ensure it's a string first
                .str.replace(r'[$,]', '', regex=True) # Remove currency symbols
                .apply(pd.to_numeric, errors='coerce') # Convert to number
                .fillna(0.0)                     # Treat empty cells as $0
            )

    # 2. CALCULATION: Apply the math
    # Ensure the Difference column exists and calculate it
    budget_df["Difference"] = budget_df["Estimated"] - budget_df["Actual"]

    # 3. DISPLAY: Show the editor with the calculated column locked
    edited_budget = st.data_editor(
        budget_df,
        num_rows="dynamic",
        key="budget_editor",
        column_config={
            "Estimated": st.column_config.NumberColumn(format="$%.2f"),
            "Actual": st.column_config.NumberColumn(format="$%.2f"),
            # Lock Difference so users don't overwrite the formula
            "Difference": st.column_config.NumberColumn(format="$%.2f", disabled=True), 
        }
    )

    # 4. LIVE METRICS (Optional but recommended)
    # This gives instant feedback since the table row won't update until you Save
    total_est = edited_budget["Estimated"].sum()
    total_act = edited_budget["Actual"].sum()
    total_diff = total_est - total_act
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Estimated", f"${total_est:,.2f}")
    c2.metric("Total Actual", f"${total_act:,.2f}")
    c3.metric("Remaining Budget", f"${total_diff:,.2f}", delta_color="normal")

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

# --- 5. SAVE CHANGES (FULL SYNC) ---
st.divider()
if st.button("💾 Save All Changes"):
    try:
        client = get_gspread_client()
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # 1. Save Budget
        budget_to_save = edited_budget.fillna(0.0)
        budget_to_save["Difference"] = budget_to_save["Estimated"] - budget_to_save["Actual"]
        b_sheet = sh.worksheet("Budget")
        b_sheet.clear()
        b_sheet.update([budget_to_save.columns.tolist()] + budget_to_save.astype(str).values.tolist())

        # 2. Save Timeline
        t_sheet = sh.worksheet("Timeline")
        t_sheet.clear()
        timeline_to_save = edited_timeline.fillna("")
        t_sheet.update([timeline_to_save.columns.tolist()] + timeline_to_save.astype(str).values.tolist())
        
        # 3. Save Todo List
        todo_sheet = sh.worksheet("Todo")
        todo_sheet.clear()
        todo_to_save = edited_todo.fillna("")
        todo_sheet.update([todo_to_save.columns.tolist()] + todo_to_save.astype(str).values.tolist())

        # 4. Save Contacts
        c_sheet = sh.worksheet("Contacts")
        c_sheet.clear()
        contacts_to_save = edited_contacts.fillna("")
        c_sheet.update([contacts_to_save.columns.tolist()] + contacts_to_save.astype(str).values.tolist())

        # 5. Save Wishlist
        w_sheet = sh.worksheet("Wishlist")
        w_sheet.clear()
        wishlist_to_save = edited_wishlist.fillna("")
        w_sheet.update([wishlist_to_save.columns.tolist()] + wishlist_to_save.astype(str).values.tolist())
        
        st.success("Successfully synced all 5 sections!")
        st.cache_data.clear() 
        
    except Exception as e:
        st.error(f"Save failed: {e}")
