import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")

# 1. JUST the ID. No "https", no "edit", no "d/"
# Double-check: Make sure there are NO spaces at the start or end of this ID string
SHEET_ID = "14j8yI42-0bmqydQCNjMvSXJr1TweapUCUvtRiXvp41I"

# 2. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Load Data - Notice we use 'spreadsheet' but pass JUST the ID
# Sometimes the library prefers the ID over the full URL
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(spreadsheet=SHEET_ID, worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=SHEET_ID, worksheet="Timeline", ttl=0)

# 4. Save Button (Update this at the bottom too!)
if st.button("☁️ Save to Cloud"):
    conn.update(spreadsheet=SHEET_ID, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=SHEET_ID, worksheet="Timeline", data=edited_timeline)
    st.session_state.budget_df = edited_budget
    st.session_state.timeline_df = edited_timeline
    st.success("Saved to Google Sheets!")
