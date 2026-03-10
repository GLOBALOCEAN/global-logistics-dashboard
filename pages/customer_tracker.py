import streamlit as st
import pandas as pd
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

st.title("Generate Customer-Specific Tracker")

# Paths (verify in File Explorer if needed)
FCL_PATH = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\Master Freight Tracker\Global Ocean Freight Tracker.xlsx"
LCL_PATH = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\LCL Tracker\LCL Tracker.xlsx"

CONSIGNEE_COL = "Consignee"  # ← change if column name is different

# Define customers FIRST – empty list on initial load, so selectbox never sees undefined variable
customers = []

# Select tracker type
tracker_type = st.selectbox("Select Tracker", ["FCL", "LCL"])

# Load customers only if a tracker is selected
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

# Customer selector – SAFE because customers is always defined above
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
    st.switch_page("../dashboard.py")