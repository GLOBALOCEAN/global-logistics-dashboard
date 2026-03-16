import streamlit as st

st.set_page_config(
    page_title="Global Ocean Logistics",
    page_icon="🌊",
    layout="wide"
)

# Branding
st.title("🌊 Global Ocean Logistics Dashboard")

st.markdown(
"""
Welcome to the **Global Ocean Logistics Operations Portal**

Use the sidebar to access:

• 📊 Global Freight Trackers  
• ✈️ MAWB Air Freight Tracker  
• 📄 Customer Shipment Trackers  

This dashboard connects your team directly to **live operational data**.
"""
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📊 Global Freight Trackers\n\nOpen FCL, LCL and AIR live sheets")

with col2:
    st.info("✈️ MAWB Tracker\n\nTrack air freight shipments")

with col3:
    st.info("📄 Customer Trackers\n\nGenerate shipment trackers for customers")
