import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="My Home Reno Planner", layout="wide")
st.title("🏗️ Cloud Reno Manager")

# Use the FULL URL, but keep it clean
SHEET_URL = "https://google.com"

# Update your read lines to use 'spreadsheet=SHEET_URL'
if 'budget_df' not in st.session_state:
    st.session_state.budget_df = conn.read(spreadsheet=SHEET_URL, worksheet="Budget", ttl=0)
if 'timeline_df' not in st.session_state:
    st.session_state.timeline_df = conn.read(spreadsheet=SHEET_URL, worksheet="Timeline", ttl=0)

# Update your Save Button at the bottom as well
if st.button("☁️ Save to Cloud"):
    conn.update(spreadsheet=SHEET_URL, worksheet="Budget", data=edited_budget)
    conn.update(spreadsheet=SHEET_URL, worksheet="Timeline", data=edited_timeline)
