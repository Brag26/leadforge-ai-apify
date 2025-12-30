import streamlit as st
import pandas as pd
import os
from apify_client import ApifyClient
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Multi-Sector Lead Generator",
    page_icon="🌍",
    layout="wide",
)

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

if not APIFY_TOKEN:
    st.error("APIFY_TOKEN is missing. Add it in Streamlit Secrets.")
    st.stop()

client = ApifyClient(APIFY_TOKEN)

ACTOR_ID = "sree_brag/multi-sector-lead-generator-actor"  # 🔁 replace with your actual Actor ID

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🌍 Multi-Sector Lead Generator")

SECTORS = [
    "Healthcare", "Dentists", "Real Estate", "Lawyers", "Restaurants",
    "Construction", "Education", "Automotive", "Finance", "Insurance",
    "IT Services", "Marketing Agencies", "Beauty & Wellness",
    "Gyms & Fitness", "Hotels", "Travel Agencies",
    "Manufacturing", "Logistics", "Retail",
    "E-commerce", "Cleaning Services",
    "Home Services", "Consultants", "Others"
]

COUNTRIES = [
    "Australia", "United States", "United Kingdom", "Canada",
    "India", "Singapore", "UAE", "New Zealand",
    "Germany", "France", "Spain", "Italy",
    "Netherlands", "Ireland", "South Africa",
    "Malaysia", "Philippines", "Indonesia",
    "Thailand", "Japan", "South Korea"
]

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
    placeholder="dentist, dental clinic\ncosmetic dentist\nimplant specialist"
)

# -------------------------------------------------
# GENERATE LEADS
# -------------------------------------------------
if st.button("🚀 Generate Leads"):
    with st.spinner("Running Apify Actor…"):
        run_input = {
            "sector": sector,
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
            st.error(f"Failed to run actor: {e}")
            st.stop()

    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------
    if not items:
        st.warning("No leads returned.")
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
        label="⬇ Download CSV",
        data=csv,
        file_name=f"leads_{sector}_{city}_{timestamp}.csv",
        mime="text/csv",
    )
