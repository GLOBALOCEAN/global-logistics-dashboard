import streamlit as st
import pandas as pd
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

# ────────────────────────────────────────────────
# Password Protection (GLOBAL / Global123!)
# ────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("Login to Global Ocean Logistics Dashboard")

    username = st.text_input("Username", type="default")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "GLOBAL" and password == "Global123!":
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Incorrect username or password")

    return False

if not check_password():
    st.stop()

# ────────────────────────────────────────────────
# Dashboard Configuration & Branding
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics Dashboard",
    page_icon="🌊",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #015486 !important; }
    .stButton > button {
        background-color: #015486;
        color: white;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #8fd8ff;
        color: #015486;
    }
    </style>
""", unsafe_allow_html=True)

# Session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar navigation
with st.sidebar:
    st.markdown("<h2 style='color:#015486;'>Global Ocean Logistics</h2>", unsafe_allow_html=True)
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    
    if st.button("📊 Global Live Sheets", use_container_width=True):
        st.session_state.page = "live_sheets"
        st.rerun()
    
    if st.button("✈️ MAWB Tracker", use_container_width=True):
        st.session_state.page = "mawb"
        st.rerun()
    
    if st.button("📄 Generate Customer Tracker", use_container_width=True):
        st.session_state.page = "customer_tracker"
        st.rerun()

# ────────────────────────────────────────────────
# Page: Home
# ────────────────────────────────────────────────
if st.session_state.page == "home":
    st.title("Global Ocean Logistics Dashboard")
    st.markdown("Select a tool below")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌍 Global Live Sheets", type="primary", use_container_width=True):
            st.session_state.page = "live_sheets"
            st.rerun()

    with col2:
        if st.button("✈️ MAWB Tracker", type="primary", use_container_width=True):
            st.session_state.page = "mawb"
            st.rerun()

    with col3:
        if st.button("📄 Generate Customer Tracker", type="primary", use_container_width=True):
            st.session_state.page = "customer_tracker"
            st.rerun()

# ────────────────────────────────────────────────
# Page: Global Live Sheets
# ────────────────────────────────────────────────
elif st.session_state.page == "live_sheets":
    st.title("Global Live Sheets")
    st.markdown("Select a tracker to open in a new tab")

    tracker_options = {
        "FCL Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B27131CEF-29EA-4236-BF36-A3CF8D102D1D%7D&file=Global%20Ocean%20Freight%20Tracker.xlsx&action=default&mobileredirect=true",
        "LCL Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B5AAFFF3D-9F8E-47E6-9755-8476A754408B%7D&file=LCL%20Tracker.xlsx&action=default&mobileredirect=true",
        "AIR Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B587EDE6D-9415-42EF-9C11-01459CB389F5%7D&file=AIR%20FREIGHT%20TRACKER.xlsx&action=default&mobileredirect=true"
    }

    selected = st.selectbox("Choose a live tracking sheet", list(tracker_options.keys()))

    if st.button(f"Open {selected}", type="primary"):
        url = tracker_options[selected]
        st.markdown(f'<a href="{url}" target="_blank">Opening {selected} in new tab...</a>', unsafe_allow_html=True)

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ────────────────────────────────────────────────
# Page: MAWB Tracker (placeholder - add your full MAWB code here)
# ────────────────────────────────────────────────
elif st.session_state.page == "mawb":
    st.title("MAWB Tracker")
    st.markdown("Track Master Air Waybills")

    # ← Paste your full MAWB tracking code here (the version with Garet font, colors, airline mapping, etc.)
    st.info("MAWB Tracker content – insert your original MAWB code here")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# ────────────────────────────────────────────────
# Page: Generate Customer-Specific Tracker
# ────────────────────────────────────────────────
elif st.session_state.page == "customer_tracker":
    st.title("Generate Customer-Specific Tracker")

    # Paths
    FCL_PATH = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\Master Freight Tracker\Global Ocean Freight Tracker.xlsx"
    LCL_PATH = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\LCL Tracker\LCL Tracker.xlsx"

    CONSIGNEE_COL = "Consignee"  # ← change if column name is different

    # Initialize customers early to avoid NameError on first load
    customers = []

    # Select tracker type
    tracker_type = st.selectbox("Select Tracker", ["FCL", "LCL"])

    # Load customers only if tracker is selected
    if tracker_type:
        path = FCL_PATH if tracker_type == "FCL" else LCL_PATH
        if not os.path.exists(path):
            st.error(f"File not found:\n{path}")
        else:
            try:
                with st.spinner(f"Loading {tracker_type} tracker..."):
                    df = pd.read_excel(path)

                if CONSIGNEE_COL not in df.columns:
                    st.error(f"Column '{CONSIGNEE_COL}' not found.\nAvailable columns:\n{list(df.columns)}")
                else:
                    customers = sorted(df[CONSIGNEE_COL].dropna().unique().tolist())
                    st.success(f"Loaded {len(customers)} unique customers from {tracker_type} tracker.")
            except Exception as e:
                st.error(f"Error loading file:\n{str(e)}\n- Close Excel if open\n- Check path")

    # Customer selector – SAFE because customers is always defined
    if customers:
        customer_name = st.selectbox("Select Customer", customers)
    else:
        customer_name = st.text_input("Enter Customer/Consignee Name (partial match)")

    if st.button("Generate & Download Tracker", type="primary"):
        if not customer_name:
            st.warning("Please select or enter a customer name first.")
        else:
            with st.spinner("Generating tracker..."):
                path = FCL_PATH if tracker_type == "FCL" else LCL_PATH
                try:
                    df = pd.read_excel(path)
                except Exception as e:
                    st.error(f"Error loading file:\n{str(e)}")
                    st.stop()

                filtered = df[df[CONSIGNEE_COL].astype(str).str.contains(customer_name, case=False, na=False)]

                if filtered.empty:
                    st.error(f"No rows found for '{customer_name}' in {tracker_type} tracker.")
                else:
                    st.success(f"Found {len(filtered)} rows for '{customer_name}' – formatting...")

                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"{tracker_type} - {customer_name[:20]}"

                    # Title row
                    title = f"MY LIFE BATHROOM {tracker_type.upper()} FREIGHT TRACKER"
                    last_col = get_column_letter(len(filtered.columns))
                    ws.merge_cells(f'A1:{last_col}1')
                    cell = ws['A1']
                    cell.value = title
                    cell.font = Font(bold=True, size=16, color="FFFFFF")
                    cell.fill = PatternFill(start_color="005566", end_color="005566", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                    # Headers
                    headers = list(filtered.columns)
                    for col_num, header in enumerate(headers, 1):
                        cell = ws.cell(row=2, column=col_num, value=header)
                        cell.font = Font(bold=True, color="FFFFFF")
                        cell.fill = PatternFill(start_color="005566", end_color="005566", fill_type="solid")
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

                    # Data rows
                    for row_num, row_data in enumerate(filtered.itertuples(index=False), 3):
                        for col_num, value in enumerate(row_data, 1):
                            cell = ws.cell(row=row_num, column=col_num, value=value)
                            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                    # Auto column widths
                    for col in ws.columns:
                        max_length = 0
                        column_letter = get_column_letter(col[0].column)
                        for cell in col:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        ws.column_dimensions[column_letter].width = max_length + 3

                    output = io.BytesIO()
                    wb.save(output)
                    output.seek(0)

                    today = datetime.now().strftime("%Y-%m-%d")
                    safe_name = customer_name.replace(' ', '_')[:30]
                    filename = f"{tracker_type}_Tracker_{safe_name}_{today}.xlsx"

                    st.download_button(
                        label=f"Download {filename}",
                        data=output,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()