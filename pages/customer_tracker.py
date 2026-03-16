import streamlit as st
import pandas as pd

st.title("📄 Customer Shipment Tracker")

uploaded_file = st.file_uploader(
    "Upload FCL or LCL Tracker",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("Preview")
    st.dataframe(df.head())

    customer_column = st.selectbox(
        "Select Customer Column",
        df.columns
    )

    customers = sorted(df[customer_column].dropna().unique())

    selected_customer = st.selectbox(
        "Select Customer",
        customers
    )

    filtered = df[df[customer_column] == selected_customer]

    st.subheader(f"{selected_customer} Shipments")

    st.dataframe(filtered)

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Customer Tracker",
        csv,
        f"{selected_customer}_tracker.csv",
        "text/csv"
    )
