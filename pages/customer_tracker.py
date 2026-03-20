import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import io

# ────────────────────────────────────────────────
# AUTH CHECK
# ────────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the main dashboard.")
    st.stop()

st.title("📄 Multi-Tracker Customer Report")

st.markdown("Upload FCL, LCL and AIR trackers to generate one combined customer report.")

# ────────────────────────────────────────────────
# FILE UPLOADS
# ────────────────────────────────────────────────
fcl_file = st.file_uploader("Upload FCL Tracker", type=["xlsx"])
lcl_file = st.file_uploader("Upload LCL Tracker", type=["xlsx"])
air_file = st.file_uploader("Upload AIR Tracker", type=["xlsx"])

# ────────────────────────────────────────────────
# LOAD DATA
# ────────────────────────────────────────────────
dfs = {}

if fcl_file:
    dfs["FCL"] = pd.read_excel(fcl_file)

if lcl_file:
    dfs["LCL"] = pd.read_excel(lcl_file)

if air_file:
    dfs["AIR"] = pd.read_excel(air_file)

if dfs:

    # Clean columns
    for key in dfs:
        dfs[key].columns = dfs[key].columns.str.strip()

    # ────────────────────────────────────────────────
    # CUSTOMER COLUMN SELECTION
    # ────────────────────────────────────────────────
    sample_df = list(dfs.values())[0]

    customer_column = st.selectbox(
        "Select Customer Column",
        sample_df.columns
    )

    # Combine customers from all files
    all_customers = set()

    for df in dfs.values():
        if customer_column in df.columns:
            all_customers.update(df[customer_column].dropna().astype(str).unique())

    selected_customer = st.selectbox(
        "Select Customer",
        sorted(all_customers)
    )

    # ────────────────────────────────────────────────
    # STATUS FILTER (ONLY IF EXISTS)
    # ────────────────────────────────────────────────
    status_options = []

    for df in dfs.values():
        if "Status" in df.columns:
            status_options.extend(df["Status"].dropna().astype(str).unique())

    status_options = sorted(set(status_options))

    selected_status = st.multiselect(
        "Filter by Status (FCL/LCL only)",
        options=status_options,
        default=status_options
    )

    # ────────────────────────────────────────────────
    # GENERATE REPORT
    # ────────────────────────────────────────────────
    if st.button("Generate Multi-Tracker Report", type="primary"):

        wb = Workbook()
        wb.remove(wb.active)

        for name, df in dfs.items():

            if customer_column not in df.columns:
                continue

            # Filter by customer
            filtered = df[
                df[customer_column]
                .astype(str)
                .str.contains(selected_customer, case=False, na=False)
            ]

            # Apply status filter if column exists
            if "Status" in df.columns:
                filtered = filtered[filtered["Status"].isin(selected_status)]

            if filtered.empty:
                continue

            ws = wb.create_sheet(title=name)

            # Headers
            for col_num, col_name in enumerate(filtered.columns, 1):
                ws.cell(row=1, column=col_num, value=col_name)

            # Status column index (if exists)
            status_index = None
            if "Status" in filtered.columns:
                status_index = filtered.columns.get_loc("Status")

            # Data
            for row_num, row_data in enumerate(filtered.itertuples(index=False), 2):

                status_value = ""
                if status_index is not None:
                    status_value = str(row_data[status_index]).strip()

                for col_num, value in enumerate(row_data, 1):

                    cell = ws.cell(row=row_num, column=col_num, value=value)

                    # Colour only if status exists
                    if status_index is not None:

                        if status_value == "In Transit":
                            cell.fill = PatternFill(start_color="C6EFCE", fill_type="solid")

                        elif status_value == "Waiting to Sail":
                            cell.fill = PatternFill(start_color="FFEB9C", fill_type="solid")

                        elif status_value == "Awaiting Confirmation":
                            cell.fill = PatternFill(start_color="BDD7EE", fill_type="solid")

                        elif status_value == "Arrived":
                            cell.fill = PatternFill(start_color="D9D9D9", fill_type="solid")

        if not wb.sheetnames:
            st.error("No data found for selected customer.")
        else:
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            filename = f"{selected_customer}_Full_Shipment_Report_{datetime.now().strftime('%d-%m-%Y')}.xlsx"

            st.download_button(
                "Download Report",
                data=output,
                file_name=filename
            )
