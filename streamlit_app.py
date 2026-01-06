import streamlit as st
import pandas as pd
import pycountry
import os
from apify_client import ApifyClient

# =================================================
# 🔐 STREAMLIT LOGIN (USES st.secrets)
# =================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 LeadForge Login")

    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")

    st.stop()

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Multi-Sector Lead Generator",
    layout="wide"
)

st.title("🌍 Multi-Sector Lead Generator")

# -------------------------------------------------
# APIFY CLIENT SETUP
# -------------------------------------------------
APIFY_TOKEN = st.secrets["APIFY_API_TOKEN"]

if not APIFY_TOKEN:
    st.error("❌ APIFY_API_TOKEN not set in secrets")
    st.stop()

client = ApifyClient(APIFY_TOKEN)

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

# -------------------------------------------------
# COUNTRIES
# -------------------------------------------------
COUNTRIES = sorted([c.name for c in pycountry.countries])

# -------------------------------------------------
# INPUT FORM (MATCHES APIFY SCHEMA)
# -------------------------------------------------
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox("Sector", SECTORS, index=0)

    with col2:
        country = st.selectbox(
            "Country (Optional)",
            COUNTRIES,
            index=COUNTRIES.index("Australia") if "Australia" in COUNTRIES else 0
        )

    with col3:
        state = st.text_input("State / Province (Optional)", "")

    col4, col5, col6 = st.columns(3)

    with col4:
        city = st.text_input("City / Suburb (Optional)", "")

    with col5:
        postcode = st.text_input("Postcode / ZIP Code (Optional)", "")

    with col6:
        max_results = st.slider(
            "Maximum Results",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )

    st.markdown("### 🔑 Keyword (Optional)")

    keyword = st.text_input(
        "Keyword",
        placeholder="clinic, software company, agency"
    )

    submitted = st.form_submit_button("🚀 Generate Leads")

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if submitted:
    with st.spinner("🚀 Running Apify actor… please wait"):
        try:
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
        except Exception as e:
            st.error(f"❌ Failed to run Apify actor: {e}")
            st.stop()

    dataset_id = run.get("defaultDatasetId")

    if not dataset_id:
        st.error("❌ No dataset returned from actor")
        st.json(run)
        st.stop()

    leads = client.dataset(dataset_id).list_items().items

    # -------------------------------------------------
    # OUTPUT
    # -------------------------------------------------
    if not leads:
        st.warning("⚠ No leads returned")
        st.stop()

    df = pd.DataFrame(leads)

    st.success(f"✅ {len(df)} leads generated")

    if keyword:
        st.info(f"🔑 Keyword used: {keyword}")

    st.subheader("🔍 Preview (first 10 results)")
    st.dataframe(df.head(10), use_container_width=True)

    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            file_name="leads.csv",
            mime="text/csv"
        )

    with col_dl2:
        st.download_button(
            "⬇ Download JSON",
            df.to_json(orient="records"),
            file_name="leads.json",
            mime="application/json"
        )

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()
