import streamlit as st
import requests
import pandas as pd
import pycountry

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Lead Generator",
    layout="wide"
)

st.title("🌍 Multi-Sector Lead Generator")

# ---------------------------------
# SECTOR LIST (24 SECTORS)
# ---------------------------------
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

# ---------------------------------
# COUNTRY LIST (ALL COUNTRIES)
# ---------------------------------
COUNTRIES = sorted([c.name for c in pycountry.countries])

# ---------------------------------
# INPUT FORM
# ---------------------------------
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox(
            "Sector",
            SECTORS,
            index=0
        )

    with col2:
        city = st.text_input("City / Suburb", "Colebee")

    with col3:
        postcode = st.text_input("Postcode", "2761")

    col4, col5 = st.columns(2)

    with col4:
        country = st.selectbox(
            "Country",
            COUNTRIES,
            index=COUNTRIES.index("Australia") if "Australia" in COUNTRIES else 0
        )

    with col5:
        max_results = st.slider(
            "Max Results",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )

    submitted = st.form_submit_button("🚀 Generate Leads")

# ---------------------------------
# ACTION
# ---------------------------------
if submitted:
    with st.spinner("Generating leads… please wait"):
        res = requests.post(
            "http://localhost:8000/generate-leads",
            json={
                "sector": sector,
                "city": city,
                "postcode": postcode,
                "country": country,
                "maxResults": max_results
            },
            timeout=300
        )

    if res.status_code != 200:
        st.error("❌ Failed to generate leads")
        st.text(res.text)
        st.stop()

    data = res.json()

    # ---------------------------------
    # NORMALIZE RESPONSE
    # ---------------------------------
    if isinstance(data, dict) and "data" in data:
        leads = data["data"]
    elif isinstance(data, list):
        leads = data
    else:
        st.warning("No leads returned")
        st.json(data)
        st.stop()

    if not leads:
        st.warning("No leads found for this search")
        st.stop()

    df = pd.DataFrame(leads)

    # ---------------------------------
    # OUTPUT UX
    # ---------------------------------
    st.success(f"✅ {len(df)} leads generated")

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
