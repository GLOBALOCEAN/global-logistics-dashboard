import streamlit as st

st.title("📊 Global Live Freight Trackers")

trackers = {
    "FCL Tracker":
    "https://netorgft11291460.sharepoint.com/...",

    "LCL Tracker":
    "https://netorgft11291460.sharepoint.com/...",

    "AIR Tracker":
    "https://netorgft11291460.sharepoint.com/..."
}

selected = st.selectbox("Select Tracker", list(trackers.keys()))

if st.button("Open Tracker"):

    url = trackers[selected]

    st.markdown(
        f'<a href="{url}" target="_blank">Open {selected}</a>',
        unsafe_allow_html=True
    )
