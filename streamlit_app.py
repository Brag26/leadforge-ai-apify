import streamlit as st
import pandas as pd
import pycountry
from apify_client import ApifyClient

# =================================================
# 🔐 MULTI-USER AUTH (STREAMLIT NATIVE)
# =================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

if not st.session_state.authenticated:
    st.set_page_config(page_title="Login | LeadForge", layout="centered")
    st.title("🔐 LeadForge Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = st.secrets["users"]

        if username in users and password == users[username]["password"]:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = users[username].get("role", "user")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()

# =================================================
# PAGE CONFIG (AFTER LOGIN)
# =================================================
st.set_page_config(
    page_title="Multi-Sector Lead Generator",
    layout="wide"
)

st.title("🌍 Multi-Sector Lead Generator")

st.sidebar.success(f"👤 Logged in as: {st.session_state.username}")
st.sidebar.caption(f"Role: {st.session_state.role}")

# -------------------------------------------------
# APIFY CLIENT
# -------------------------------------------------
client = ApifyClient(st.secrets["APIFY_API_TOKEN"])
ACTOR_ID = "sree_brag/multi-sector-lead-generator-actor"

# -------------------------------------------------
# SECTORS
# -------------------------------------------------
SECTORS = [
    "Healthcare",
    "Real Estate",
    "Manufacturing",
    "IT & Technology",
    "Education & Training",
    "Legal Services",
    "Financial Services",
    "Hospitality & Tourism",
    "Retail & E-commerce",
    "Food & Beverage",
    "Construction",
    "Automotive",
    "Marketing & Advertising",
    "Consulting",
    "Logistics & Transportation",
    "Beauty & Wellness",
    "Entertainment & Media",
    "Agriculture",
    "Energy & Utilities",
    "Telecommunications",
    "Insurance",
    "Professional Services",
    "Non-Profit & NGO",
    "Sports & Fitness"
]

COUNTRIES = sorted([c.name for c in pycountry.countries])

# -------------------------------------------------
# INPUT FORM
# -------------------------------------------------
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox("Sector", SECTORS)

    with col2:
        country = st.selectbox(
            "Country",
            COUNTRIES,
            index=COUNTRIES.index("Australia") if "Australia" in COUNTRIES else 0
        )

    with col3:
        state = st.text_input("State / Province")

    col4, col5, col6 = st.columns(3)

    with col4:
        city = st.text_input("City / Suburb")

    with col5:
        postcode = st.text_input("Postcode / ZIP Code")

    with col6:
        max_results = st.slider("Max Results", 1, 100, 10)

    keyword = st.text_input("Keyword (Optional)")
    submitted = st.form_submit_button("🚀 Generate Leads")

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if submitted:
    with st.spinner("🚀 Running Apify actor…"):
        run = client.actor(ACTOR_ID).call(
            run_input={
                "sector": sector,
                "country": country,
                "state": state,
                "city": city,
                "postcode": postcode,
                "keyword": keyword,
                "maxResults": max_results
            },
            timeout_secs=180
        )

    dataset_id = run.get("defaultDatasetId")
    leads = client.dataset(dataset_id).list_items().items

    if not leads:
        st.warning("No leads found")
        st.stop()

    df = pd.DataFrame(leads)
    st.success(f"✅ {len(df)} leads generated")
    st.dataframe(df.head(10), use_container_width=True)

    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False),
        "leads.csv",
        "text/csv"
    )

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()
