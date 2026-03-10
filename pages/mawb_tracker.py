import streamlit as st
import requests
from datetime import datetime

# GOL Branding + Garet font + colors
st.markdown("""
    <link href="https://cdn.jsdelivr.net/gh/type-forward/garet@latest/fonts/webfonts/garet.css" rel="stylesheet">
    <style>
    .gol-header {
        font-family: 'Garet', 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        text-align: center !important;
        margin: 1.5rem 0 0.5rem !important;
    }
    .gol-header .global, .gol-header .logistics {
        color: #015486 !important;
    }
    .gol-header .ocean {
        color: #8fd8ff !important;
    }
    .gol-tagline {
        color: #8fd8ff !important;
        font-size: 1.45rem !important;
        text-align: center !important;
        margin-bottom: 2.5rem !important;
    }
    .result-card {
        background-color: white !important;
        border: 1px solid #8fd8ff !important;
        border-left: 6px solid #015486 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08) !important;
        margin: 2rem 0 2.5rem !important;
    }
    .stButton > button {
        background-color: #015486 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        max-width: 420px !important;
        margin: 2rem auto 1rem !important;
        display: block !important;
    }
    .stButton > button:hover {
        background-color: #8fd8ff !important;
        color: #015486 !important;
    }
    .stSuccess, .stInfo, .stError {
        border-radius: 8px !important;
        padding: 1.2rem !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid #8fd8ff !important;
        border-radius: 10px !important;
        padding: 0.9rem !important;
    }
    .gol-footer {
        text-align: center !important;
        color: #444 !important;
        font-size: 0.95rem !important;
        margin-top: 5rem !important;
        padding: 1.8rem !important;
        border-top: 1px solid #eee !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="gol-header">
        <span class="global">Global</span>
        <span class="ocean">Ocean</span>
        <span class="logistics">Logistics</span>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="gol-tagline">Air Freight Tracker – Fast, Reliable, Global</div>', unsafe_allow_html=True)

st.markdown("Enter your **Master Air Waybill (MAWB)** number to track your shipment.")

# Airline mapping
PREFIX_MAP = {
    "020": {"name": "Lufthansa Cargo", "code": "LH", "has_api": True},
    "999": {"name": "Air China Cargo", "code": "CA", "has_api": False},
    "784": {"name": "China Southern Cargo", "code": "CZ", "has_api": False},
    "781": {"name": "China Eastern Cargo", "code": "MU", "has_api": False},
    "160": {"name": "Cathay Pacific Cargo", "code": "CX", "has_api": False},
    "180": {"name": "Korean Air Cargo", "code": "KE", "has_api": False},
    "695": {"name": "EVA Air Cargo", "code": "BR", "has_api": False},
}

# Parse MAWB
def parse_mawb(mawb_str):
    cleaned = ''.join(c for c in str(mawb_str) if c.isdigit())
    if len(cleaned) not in (10, 11):
        return None, None
    prefix = cleaned[:3]
    number = cleaned[3:]
    return prefix, number

# Tracking link generator
def get_tracking_link(airline_name, prefix, number):
    full_awb = f"{prefix}-{number}" if len(number) == 8 else f"{prefix}{number}"
   
    if "Air China" in airline_name:
        return "https://www.airchinacargo.com/cargo_en/gzcx/hkyd/list/index_pc.html", full_awb
   
    if "China Southern" in airline_name:
        return f"https://tang.csair.com/EN/WebFace/Tang.WebFace.Cargo/AgentAwbBrower.aspx?lan=en-us&AWB={full_awb}", full_awb
   
    if "Cathay Pacific" in airline_name:
        return f"https://www.cathaycargo.com/en-us/track-and-trace.html?awb={full_awb}", full_awb
   
    # Fallback Google search
    return f"https://www.google.com/search?q={airline_name.replace(' ', '+')}+cargo+tracking+{full_awb}", full_awb

# Main UI
mawb_input = st.text_input(
    "MAWB Number",
    placeholder="e.g. 999-38712203 or 020-08002050",
    help="With or without dashes / spaces"
)

if st.button("Track Shipment"):
    prefix, number = parse_mawb(mawb_input)
   
    if not prefix or not number:
        st.error("Invalid MAWB – please enter 10 or 11 digits.")
    else:
        airline = PREFIX_MAP.get(prefix, {"name": f"Carrier ({prefix})", "code": prefix, "has_api": False})
       
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
       
        st.success(f"**Detected:** {airline['name']} ({airline['code']}) – AWB **{prefix}-{number}**")
       
        if airline.get("has_api", False) and prefix == "020":
            st.info("Querying Lufthansa Cargo API…")
        else:
            url, full_awb = get_tracking_link(airline["name"], prefix, number)
           
            st.markdown(f"""
                <p style="font-size:1.15rem; margin: 1.8rem 0 1rem; color: #333;">
                    Open official tracking for this shipment:
                </p>
            """, unsafe_allow_html=True)
           
            st.markdown(f"""
                <a href="{url}" target="_blank" style="
                    background-color: #015486;
                    color: white;
                    padding: 16px 36px;
                    text-decoration: none;
                    border-radius: 10px;
                    font-size: 1.25rem;
                    font-weight: bold;
                    display: inline-block;
                ">
                    Open {airline['name']} Tracking → {full_awb}
                </a>
            """, unsafe_allow_html=True)
           
            st.caption("Click the blue button above to open in a new tab.")
       
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="gol-footer">
        © Global Ocean Logistics NI • Air & Sea Freight Solutions<br>
        Belfast / Newtownards • contact@globaloceanlogisticsni.com
    </div>
""", unsafe_allow_html=True)