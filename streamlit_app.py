import streamlit as st
import requests
import pandas as pd
import pycountry

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Multi-LLM AI-Powered Lead Generator",
    layout="wide"
)

st.title("🌍 Multi-LLM AI-Powered Lead Generator")

# -------------------------------------------------
# SECTORS (24) — must match input_schema.json
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
# INPUT FORM (SCHEMA MATCHED)
# -------------------------------------------------
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox("Sector", SECTORS)

    with col2:
        country = st.selectbox(
            "Country (Optional)",
            [""] + COUNTRIES,
            index=COUNTRIES.index("Australia") + 1 if "Australia" in COUNTRIES else 0
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
            value=10
        )

    st.markdown("### 🔑 Keyword (Optional)")

    keyword = st.text_input(
        "Keyword to refine search",
        placeholder="e.g., dental clinic, software company"
    )

    submitted = st.form_submit_button("🚀 Generate Leads")

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if submitted:
    payload = {
        "sector": sector,
        "country": country,
        "state": state,
        "city": city,
        "postcode": postcode,
        "keyword": keyword,
        "maxResults": max_results
    }

    # remove empty optional fields
    payload = {k: v for k, v in payload.items() if v not in ["", None]}

    with st.spinner("Generating leads… please wait"):
        try:
            res = requests.post(
                "http://localhost:8000/generate-leads",
                json=payload,
                timeout=300
            )
        except Exception as e:
            st.error(f"❌ Backend connection failed: {e}")
            st.stop()

    if res.status_code != 200:
        st.error("❌ Failed to generate leads")
        st.text(res.text)
        st.stop()

    data = res.json()

    # -------------------------------------------------
    # NORMALIZE RESPONSE
    # -------------------------------------------------
    if isinstance(data, dict) and "leads" in data:
        leads = data["leads"]
    elif isinstance(data, dict) and "data" in data:
        leads = data["data"]
    elif isinstance(data, list):
        leads = data
    else:
        leads = []

    if not leads:
        st.warning("No leads returned")
        st.json(data)
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
