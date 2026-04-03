import streamlit as st
import pandas as pd
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

st.title("Generate Customer-Specific Tracker")

st.markdown("""
Select the tracker and customer below to generate a formatted spreadsheet.
""")

# Select tracker
tracker_type = st.selectbox("Select Tracker", ["FCL", "LCL", "AIR"])

# Define paths
if tracker_type == "FCL":
    path = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\Master Freight Tracker\Global Ocean Freight Tracker.xlsx"
elif tracker_type == "LCL":
    path = r"C:\Users\Paul\globaloceanlogisticsni.com\Global SharePoint - Documents\TRACKERS\LCL Tracker\LCL Tracker.xlsx"
else:
    path = None  # AIR - add path later if needed

if path and os.path.exists(path):
    try:
        df = pd.read_excel(path)
        st.success("Tracker loaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    # Column selection
    consignee_col = st.selectbox("Consignee Column", options=list(df.columns))

    if consignee_col in df.columns:
        customers = sorted(df[consignee_col].dropna().unique().tolist())
        customer_name = st.selectbox("Select Customer", customers)

        if st.button("Generate & Download", type="primary"):
            with st.spinner("Generating..."):
                filtered = df[df[consignee_col].astype(str).str.contains(customer_name, case=False, na=False)]

                if filtered.empty:
                    st.error("No rows found for this customer.")
                else:
                    st.success(f"Found {len(filtered)} rows – creating file...")

                    wb = Workbook()
                    ws = wb.active
                    ws.title = f"{tracker_type} - {customer_name[:20]}"

                    title = f"MY LIFE BATHROOM {tracker_type.upper()} FREIGHT TRACKER"
                    last_col = get_column_letter(len(filtered.columns))
                    ws.merge_cells(f'A1:{last_col}1')
                    cell = ws['A1']
                    cell.value = title
                    cell.font = Font(bold=True, size=16, color="FFFFFF")
                    cell.fill = PatternFill(start_color="005566", end_color="005566", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")

                    headers = list(filtered.columns)
                    for col_num, header in enumerate(headers, 1):
                        cell = ws.cell(row=2, column=col_num, value=header)
                        cell.font = Font(bold=True, color="FFFFFF")
                        cell.fill = PatternFill(start_color="005566", end_color="005566", fill_type="solid")
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

                    for row_num, row_data in enumerate(filtered.itertuples(index=False), 3):
                        for col_num, value in enumerate(row_data, 1):
                            cell = ws.cell(row=row_num, column=col_num, value=value)
                            cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

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
    else:
        st.error(f"Column '{consignee_col}' not found in the file.")
else:
    st.error("Tracker file not found or path is incorrect. Please check the path in the code.")

if st.button("← Back to Home"):
    st.switch_page("../dashboard.py")
