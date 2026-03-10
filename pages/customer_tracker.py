import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

st.title("Generate Customer-Specific Tracker")

st.markdown("""
**How to use:**
1. Upload your LCL or FCL tracker Excel file (the one you normally open from SharePoint)
2. Select the column that contains customer/consignee names
3. Choose the customer you want a tracker for
4. Click Generate — it will download a formatted version with only that customer's rows
""")

uploaded_file = st.file_uploader(
    "Upload Tracker Excel File",
    type=["xlsx", "xls"],
    help="This should be your full LCL or FCL tracker from SharePoint"
)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded and loaded successfully!")
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        st.stop()

    # Let user choose the consignee column
    possible_cols = list(df.columns)
    consignee_col = st.selectbox(
        "Select the Consignee / Customer Column",
        possible_cols,
        index=possible_cols.index("Consignee") if "Consignee" in possible_cols else 0
    )

    if consignee_col not in df.columns:
        st.error(f"Column '{consignee_col}' not found in uploaded file.")
    else:
        # Get unique customers from uploaded file
        customers = sorted(df[consignee_col].dropna().unique().tolist())
        if not customers:
            st.warning("No customer names found in the selected column.")
        else:
            customer_name = st.selectbox("Select Customer", customers)

            # Tracker type for title
            tracker_type = st.selectbox("Tracker Type (used in title)", ["LCL", "FCL"])

            if st.button("Generate & Download Formatted Tracker", type="primary"):
                if not customer_name:
                    st.warning("Please select a customer first.")
                else:
                    with st.spinner("Creating formatted tracker..."):
                        filtered = df[df[consignee_col].astype(str).str.contains(customer_name, case=False, na=False)]

                        if filtered.empty:
                            st.error(f"No rows found for '{customer_name}'")
                        else:
                            st.success(f"Found {len(filtered)} rows for '{customer_name}'")

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
    st.info("Upload your tracker file to get started.")

if st.button("← Back to Home"):
    st.switch_page("../dashboard.py")
