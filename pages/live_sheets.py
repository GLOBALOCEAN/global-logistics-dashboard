import streamlit as st

st.title("Global Live Sheets")
st.markdown("Select a tracker to open in a new browser tab")

trackers = {
    "FCL Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B27131CEF-29EA-4236-BF36-A3CF8D102D1D%7D&file=Global%20Ocean%20Freight%20Tracker.xlsx&action=default&mobileredirect=true",
    "LCL Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B5AAFFF3D-9F8E-47E6-9755-8476A754408B%7D&file=LCL%20Tracker.xlsx&action=default&mobileredirect=true",
    "AIR Tracker": "https://netorgft11291460.sharepoint.com/:x:/r/sites/GlobalSharePoint/_layouts/15/Doc.aspx?sourcedoc=%7B587EDE6D-9415-42EF-9C11-01459CB389F5%7D&file=AIR%20FREIGHT%20TRACKER.xlsx&action=default&mobileredirect=true"
}

selected = st.selectbox("Choose a live tracking sheet", list(trackers.keys()))

if st.button(f"Open {selected}", type="primary"):
    url = trackers[selected]
    st.markdown(f'<a href="{url}" target="_blank">Opening {selected} in new tab...</a>', unsafe_allow_html=True)

if st.button("← Back to Dashboard"):
    st.switch_page("../dashboard.py")