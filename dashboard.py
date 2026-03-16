import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

# ────────────────────────────────────────────────
# Password Protection
# ────────────────────────────────────────────────
def check_password():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("Login to Global Ocean Logistics Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "GLOBAL" and password == "Global123!":
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Incorrect username or password")

    return False


if not check_password():
    st.stop()


# ────────────────────────────────────────────────
# Page Config
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics Dashboard",
    page_icon="🌊",
    layout="wide"
)


# ────────────────────────────────────────────────
# Styling
# ────────────────────────────────────────────────
st.markdown(
"""
<style>

.stApp {
    background-color: #f8f9fa;
}

h1, h2, h3 {
    color: #015486 !important;
}

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
""",
unsafe_allow_html=True
)


# ────────────────────────────────────────────────
# Navigation
# ────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"


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
# HOME PAGE
# ────────────────────────────────────────────────
if st.session_state.page == "home":

    st.title("Global Ocean Logistics Dashboard")
    st.write("Select a tool below")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌍 Global Live Sheets", use_container_width=True):
            st.session_state.page = "live_sheets"
            st.rerun()

    with col2:
        if st.button("✈️ MAWB Tracker", use_container_width=True):
            st.session_state.page = "mawb"
            st.rerun()

    with col3:
        if st.button("📄 Generate Customer Tracker", use_container_width=True):
            st.session_state.page = "customer_tracker"
            st.rerun()


# ────────────────────────────────────────────────
# LIVE SHEETS PAGE
# ────────────────────────────────────────────────
elif st.session_state.page == "live_sheets":

    st.title("Global Live Sheets")

    trackers = {
        "FCL Tracker":
        "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B27131CEF-29EA-4236-BF36-A3CF8D102D1D%7D",

        "LCL Tracker":
        "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B5AAFFF3D-9F8E-47E6-9755-8476A754408B%7D",

        "AIR Tracker":
        "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B587EDE6D-9415-42EF-9C11-01459CB389F5%7D"
    }

    selected = st.selectbox("Choose tracker", list(trackers.keys()))

    if st.button("Open Tracker", type="primary"):
        url = trackers[selected]
        st.markdown(f'<a href="{url}" target="_blank">Open {selected}</a>', unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()


# ────────────────────────────────────────────────
# MAWB PAGE (placeholder)
# ────────────────────────────────────────────────
elif st.session_state.page == "mawb":

    st.title("MAWB Tracker")
    st.info("Insert your MAWB tracker code here")

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()


# ────────────────────────────────────────────────
# CUSTOMER TRACKER PAGE
# ────────────────────────────────────────────────
elif st.session_state.page == "customer_tracker":

    st.title("Generate Customer Tracker")

    uploaded_file = st.file_uploader(
        "Upload FCL or LCL Tracker",
        type=["xlsx"]
    )

    if uploaded_file:

        df = pd.read_excel(uploaded_file)

        st.subheader("Preview")
        st.dataframe(df.head())

        df.columns = df.columns.str.strip()

        customer_column = st.selectbox(
            "Select Customer Column",
            df.columns
        )

        customers = sorted(df[customer_column].dropna().astype(str).unique())

        selected_customer = st.selectbox(
            "Select Customer",
            customers
        )

        tracker_type = st.selectbox(
            "Tracker Type",
            ["FCL", "LCL"]
        )

        if st.button("Generate Tracker", type="primary"):

            filtered = df[
                df[customer_column]
                .astype(str)
                .str.contains(selected_customer, case=False, na=False)
            ]

            if filtered.empty:

                st.error("No records found")

            else:

                wb = Workbook()
                ws = wb.active

                title = f"{selected_customer} {tracker_type} Freight Tracker"

                last_col = get_column_letter(len(filtered.columns))
                ws.merge_cells(f"A1:{last_col}1")

                cell = ws["A1"]
                cell.value = title
                cell.font = Font(bold=True, size=16, color="FFFFFF")
                cell.fill = PatternFill(start_color="005566", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

                headers = list(filtered.columns)

                for col_num, header in enumerate(headers, 1):
                    ws.cell(row=2, column=col_num, value=header)

                for row_num, row_data in enumerate(filtered.itertuples(index=False), 3):
                    for col_num, value in enumerate(row_data, 1):
                        ws.cell(row=row_num, column=col_num, value=value)

                output = io.BytesIO()
                wb.save(output)
                output.seek(0)

                today = datetime.now().strftime("%Y-%m-%d")
                filename = f"{tracker_type}_{selected_customer}_{today}.xlsx"

                st.download_button(
                    "Download Tracker",
                    data=output,
                    file_name=filename
                )

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()
