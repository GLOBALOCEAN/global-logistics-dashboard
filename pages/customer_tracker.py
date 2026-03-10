import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

st.title("Generate Customer-Specific Tracker")

st.markdown("""
Upload your LCL or FCL tracker Excel file below.  
The script will read it from memory (no local paths needed),  
let you select the customer column and name, then generate a formatted version.
""")

uploaded_file = st.file_uploader(
    "Upload Tracker Excel File",
    type=["xlsx", "xls"],
    help="Must be your LCL or FCL tracker file from SharePoint"
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded and read successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Let user choose the consignee column
    possible_cols = list(df.columns)
    consignee_col = st.selectbox(
        "Consignee / Customer Column",
        possible_cols,
        index=possible_cols.index("Consignee") if "Consignee" in possible_cols else 0
    )

    if consignee_col not in df.columns:
        st.error(f"Column '{consignee_col}' not found in file.")
    else:
        customers = sorted(df[consignee_col].dropna().unique().tolist())
        if not customers:
            st.warning("No customer names found in selected column.")
        else:
            customer_name = st.selectbox("Select Customer", customers)

            tracker_type = st.selectbox("Tracker Type (for title)", ["LCL", "FCL"])

            if st.button("Generate & Download", type="primary"):
                with st.spinner("Creating formatted tracker..."):
                    filtered = df[df[consignee_col].astype(str).str.contains(customer_name, case=False, na=False)]

                    if filtered.empty:
                        st.error(f"No rows found for '{customer_name}'")
                    else:
                        st.success(f"Found {len(filtered)} rows – formatting Excel...")

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
else:
    st.info("Upload your tracker Excel file to start generating customer versions.")

if st.button("← Back to Home"):
    st.switch_page("../dashboard.py")
