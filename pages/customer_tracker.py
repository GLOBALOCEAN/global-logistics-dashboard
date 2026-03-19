import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

# ────────────────────────────────────────────────
# AUTH CHECK (REDIRECT IF NOT LOGGED IN)
# ────────────────────────────────────────────────
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Redirecting to login...")
    st.switch_page("dashboard.py")
    st.stop()

# ────────────────────────────────────────────────
# PAGE TITLE
# ────────────────────────────────────────────────
st.title("📄 Customer Shipment Tracker")

st.markdown("""
Upload your **FCL or LCL tracker**, select a customer, filter by status, and download a **formatted tracker**.
""")

# ────────────────────────────────────────────────
# FILE UPLOAD
# ────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload Tracker Excel File",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    st.subheader("Preview")
    st.dataframe(df.head())

    # ────────────────────────────────────────────────
    # SELECT CUSTOMER COLUMN
    # ────────────────────────────────────────────────
    customer_column = st.selectbox(
        "Select Customer Column",
        df.columns
    )

    # ────────────────────────────────────────────────
    # SELECT CUSTOMER
    # ────────────────────────────────────────────────
    customers = sorted(df[customer_column].dropna().astype(str).unique())

    selected_customer = st.selectbox(
        "Select Customer",
        customers
    )

    # ────────────────────────────────────────────────
    # STATUS CHECK + FILTER
    # ────────────────────────────────────────────────
    if "Status" not in df.columns:
        st.error("No 'Status' column found in file.")
        st.stop()

    status_options = sorted(df["Status"].dropna().astype(str).unique())

    selected_status = st.multiselect(
        "Filter by Status",
        options=status_options,
        default=status_options
    )

    # ────────────────────────────────────────────────
    # TRACKER TYPE
    # ────────────────────────────────────────────────
    tracker_type = st.selectbox(
        "Tracker Type",
        ["FCL", "LCL"]
    )

    # ────────────────────────────────────────────────
    # GENERATE TRACKER
    # ────────────────────────────────────────────────
    if st.button("Generate & Download Tracker", type="primary"):

        filtered = df[
            (df[customer_column]
             .astype(str)
             .str.contains(selected_customer, case=False, na=False)) &
            (df["Status"].isin(selected_status))
        ]

        if filtered.empty:
            st.error("No matching records found.")

        else:
            st.success(f"{len(filtered)} rows found")

            wb = Workbook()
            ws = wb.active
            ws.title = f"{tracker_type} - {selected_customer[:20]}"

            # ────────────────────────────────────────────────
            # TITLE ROW
            # ────────────────────────────────────────────────
            title = f"GLOBAL OCEAN LOGISTICS - {tracker_type} SHIPMENT TRACKER"
            last_col = get_column_letter(len(filtered.columns))

            ws.merge_cells(f"A1:{last_col}1")

            cell = ws["A1"]
            cell.value = title
            cell.font = Font(bold=True, size=16, color="FFFFFF")
            cell.fill = PatternFill(start_color="005566", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

            # Info rows
            ws["A2"] = f"Customer: {selected_customer}"
            ws["A3"] = f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}"

            # ────────────────────────────────────────────────
            # HEADERS
            # ────────────────────────────────────────────────
            headers = list(filtered.columns)

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num, value=header)

                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="005566", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", wrap_text=True)
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )

            # ────────────────────────────────────────────────
            # DATA + COLOUR CODING
            # ────────────────────────────────────────────────
            status_index = filtered.columns.get_loc("Status")

            for row_num, row_data in enumerate(filtered.itertuples(index=False), 6):

                status_value = str(row_data[status_index]).strip()

                for col_num, value in enumerate(row_data, 1):

                    cell = ws.cell(row=row_num, column=col_num, value=value)

                    # Colour based on status
                    if status_value == "In Transit":
                        cell.fill = PatternFill(start_color="C6EFCE", fill_type="solid")

                    elif status_value == "Waiting to Sail":
                        cell.fill = PatternFill(start_color="FFEB9C", fill_type="solid")

                    elif status_value == "Awaiting Confirmation":
                        cell.fill = PatternFill(start_color="BDD7EE", fill_type="solid")

                    elif status_value == "Arrived":
                        cell.fill = PatternFill(start_color="D9D9D9", fill_type="solid")

                    cell.border = Border(
                        left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin')
                    )

                    cell.alignment = Alignment(horizontal="center", wrap_text=True)

            # ────────────────────────────────────────────────
            # AUTO COLUMN WIDTH
            # ────────────────────────────────────────────────
            for col in ws.columns:
                max_length = 0
                column_letter = get_column_letter(col[0].column)

                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass

                ws.column_dimensions[column_letter].width = max_length + 3

            # ────────────────────────────────────────────────
            # EXPORT FILE
            # ────────────────────────────────────────────────
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            today = datetime.now().strftime("%d-%m-%Y")
            safe_name = selected_customer.replace(" ", "_")

            filename = f"{safe_name}_{tracker_type}_Shipment_Tracker_{today}.xlsx"

            st.download_button(
                label="Download Tracker",
                data=output,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
