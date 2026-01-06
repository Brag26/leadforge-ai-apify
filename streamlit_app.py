import streamlit as st
import pandas as pd
from apify_client import ApifyClient
from datetime import datetime

# -------------------------------------------------
# LOGIN / AUTH
# -------------------------------------------------
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.title("🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = st.secrets["users"]

        if username in users and password == users[username]["password"]:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()


check_login()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Multi-Sector Lead Generator",
    page_icon="🌍",
    layout="wide",
)

# -------------------------------------------------
# APIFY CONFIG
# -------------------------------------------------
APIFY_TOKEN = st.secrets.get("APIFY_TOKEN")

if not APIFY_TOKEN:
    st.error("APIFY_TOKEN is missing in Streamlit Secrets.")
    st.stop()

client = ApifyClient(APIFY_TOKEN)

ACTOR_ID = "sree_brag/multi-sector-lead-generator-actor"

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🌍 Multi-Sector Lead Generator")
st.caption(f"Logged in as **{st.session_state.username}** ({st.session_state.role})")

if st.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# -------------------------------------------------
# SECTORS (⚠️ EXACT ENUM MATCH)
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

COUNTRIES = [
    "Australia", "United States", "United Kingdom", "Canada",
    "India", "Singapore", "UAE", "New Zealand",
    "Germany", "France", "Spain", "Italy",
    "Netherlands", "Ireland", "South Africa",
    "Malaysia", "Philippines", "Indonesia",
    "Thailand", "Japan", "South Korea"
]

# -------------------------------------------------
# INPUT UI
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    sector = st.selectbox("Sector", SECTORS)

with col2:
    city = st.text_input("City / Suburb", value="Colebee")

with col3:
    postcode = st.text_input("Postcode", value="2761")

col4, col5 = st.columns([2, 3])

with col4:
    country = st.selectbox("Country", COUNTRIES)

with col5:
    max_results = st.slider("Max Results", 10, 300, 100)

st.markdown("### 🔑 Keywords (Optional)")
keywords = st.text_area(
    "Enter keywords (comma or new line separated)",
    placeholder="clinic, company, services\nlocal business"
)

# -------------------------------------------------
# GENERATE LEADS
# -------------------------------------------------
if st.button("🚀 Generate Leads"):
    with st.spinner("Running Apify Actor…"):
        run_input = {
            "sector": sector,              # ✅ Enum-safe
            "city": city.strip(),
            "postcode": postcode.strip(),
            "country": country,
            "maxResults": max_results,
            "keyword": keywords.strip(),
        }

        try:
            run = client.actor(ACTOR_ID).call(run_input=run_input)
            dataset_id = run["defaultDatasetId"]
            items = list(client.dataset(dataset_id).iterate_items())

        except Exception as e:
            st.error(f"❌ Actor execution failed: {e}")
            st.stop()

    if not items:
        st.warning("⚠️ No leads returned.")
        st.stop()

    df = pd.DataFrame(items)

    st.success(f"✅ {len(df)} leads found")
    st.dataframe(df, use_container_width=True)

    # -------------------------------------------------
    # DOWNLOAD
    # -------------------------------------------------
    csv = df.to_csv(index=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    st.download_button(
        "⬇ Download CSV",
        csv,
        f"leads_{sector}_{city}_{timestamp}.csv",
        "text/csv",
    )
