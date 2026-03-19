import streamlit as st

# ────────────────────────────────────────────────
# PASSWORD PROTECTION
# ────────────────────────────────────────────────
def check_password():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("Login to Global Ocean Logistics Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "GLOBAL" and password == "Global123!":
            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("Incorrect username or password")

    return False


if not check_password():
    st.stop()


# ────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Ocean Logistics",
    page_icon="🌊",
    layout="wide"
)

# ────────────────────────────────────────────────
# DASHBOARD CONTENT
# ────────────────────────────────────────────────
st.title("🌊 Global Ocean Logistics Dashboard")

st.markdown("""
Welcome to the **Global Ocean Logistics Operations Portal**

Use the sidebar to navigate between tools.
""")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Global Freight Trackers")
    st.write("Access live FCL, LCL and AIR trackers.")

with col2:
    st.subheader("✈️ MAWB Tracker")
    st.write("Track air freight shipments.")

with col3:
    st.subheader("📄 Customer Tracker")
    st.write("Generate shipment trackers for customers.")
