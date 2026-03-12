import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

st.title("Generate Customer-Specific Tracker")

st.markdown("""
**Step-by-step:**
1. Upload your LCL or FCL tracker Excel file (the full one from SharePoint)
2. Select the column with customer/consignee names
3. Choose the customer
4. Select LCL or FCL for the title
5. Click Generate — it will download the formatted tracker with only that customer's rows
""")

uploaded_file = st.file_uploader(
    "Upload LCL or FCL Tracker Excel File",
    type=["xlsx", "xls"],
    help="Drag & drop or click to browse. This is the file you normally open from SharePoint."
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        # FIX 1: remove hidden Excel column spacing
        df.columns = df.columns.str.strip()

        st.success("File uploaded and loaded successfully!")

        st.subheader("Preview of Uploaded Data")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Column selection
    consignee_col = st.selectbox(
        "Consignee / Customer Column",
        options=list(df.columns),
        index=list(df.columns).index("Consignee") if "Consignee" in df.columns else 0
    )

    if consignee_col not in df.columns:
        st.error(f"Column '{consignee_col}' not found in uploaded file.")
    else:

        customers = sorted(df[consignee_col].dropna().astype(str).unique().tolist())

        if not customers:
            st.warning("No customer names found in the selected column.")
        else:

            customer_name = st.selectbox("Select Customer", customers)

            tracker_type = st.selectbox(
                "Tracker Type (for title)",
                ["LCL", "FCL"]
            )

            if st.button("Generate & Download", type="primary"):

                with st.spinner("Generating formatted tracker..."):

                    filtered = df[
                        df[consignee_col]
                        .astype(str)
                        .str.contains(customer_name, case=False, na=False)
                    ]

                    if filtered.empty:
                        st.error(f"No rows found for '{customer_name}'")
                    else:

                        st.success(f"Found {len(filtered)} rows")

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
                        cell.fill = PatternFill(
                            start_color="005566",
                            end_color="005566",
                            fill_type="solid"
                        )
                        cell.alignment = Alignment(horizontal="center", vertical="center")

                        # Header row
                        headers = list(filtered.columns)

                        for col_num, header in enumerate(headers, 1):
                            cell = ws.cell(row=2, column=col_num, value=header)

                            cell.font = Font(bold=True, color="FFFFFF")

                            cell.fill = PatternFill(
                                start_color="005566",
                                end_color="005566",
                                fill_type="solid"
                            )

                            cell.alignment = Alignment(
                                horizontal="center",
                                vertical="center",
                                wrap_text=True
                            )

                            cell.border = Border(
                                left=Side(style='thin'),
                                right=Side(style='thin'),
                                top=Side(style='thin'),
                                bottom=Side(style='thin')
                            )

                        # Data rows
                        for row_num, row_data in enumerate(filtered.itertuples(index=False), 3):

                            for col_num, value in enumerate(row_data, 1):

                                cell = ws.cell(row=row_num, column=col_num, value=value)

                                cell.border = Border(
                                    left=Side(style='thin'),
                                    right=Side(style='thin'),
                                    top=Side(style='thin'),
                                    bottom=Side(style='thin')
                                )

                                cell.alignment = Alignment(
                                    horizontal="center",
                                    vertical="center",
                                    wrap_text=True
                                )

                        # FIX 2: safer auto column width
                        for i, column in enumerate(ws.columns, 1):

                            max_length = 0
                            column_letter = get_column_letter(i)

                            for cell in column:
                                try:
                                    if cell.value:
                                        max_length = max(
                                            max_length,
                                            len(str(cell.value))
                                        )
                                except:
                                    pass

                            ws.column_dimensions[column_letter].width = max_length + 3

                        # Save to memory
                        output = io.BytesIO()
                        wb.save(output)
                        output.seek(0)

                        # Filename
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
    st.info("Upload your tracker file to start generating.")

# Navigation button
if st.button("← Back to Home"):
    st.switch_page("../dashboard.py")
