import streamlit as st
import requests
import pandas as pd
import pycountry

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Multi-Sector Lead Generator",
    layout="wide"
)

st.title("🌍 Multi-Sector Lead Generator")

# -------------------------------------------------
# SECTORS (24)
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
# COUNTRIES (ALL)
# -------------------------------------------------
COUNTRIES = sorted([c.name for c in pycountry.countries])

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def parse_keywords(text: str):
    if not text:
        return []
    raw = text.replace("\n", ",").split(",")
    return [k.strip() for k in raw if k.strip()]

# -------------------------------------------------
# INPUT FORM
# -------------------------------------------------
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        sector = st.selectbox("Sector", SECTORS, index=0)

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

    # -------------------------------------------------
    # KEYWORDS SECTION (NEW)
    # -------------------------------------------------
    st.markdown("### 🔑 Keywords (Optional)")

    keywords_input = st.text_area(
        "Enter keywords (comma or new line separated)",
        placeholder="dentist, dental clinic\ncosmetic dentist\nimplant specialist"
    )

    submitted = st.form_submit_button("🚀 Generate Leads")

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if submitted:
    keywords = parse_keywords(keywords_input)

    with st.spinner("Generating leads… please wait"):
        try:
            res = requests.post(
                "http://localhost:8000/generate-leads",
                json={
                    "sector": sector,
                    "city": city,
                    "postcode": postcode,
                    "country": country,
                    "keywords": keywords,   # 👈 added to payload
                    "maxResults": max_results
                },
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
    # NORMALIZE BACKEND RESPONSE (CRITICAL FIX)
    # -------------------------------------------------
    if isinstance(data, dict) and "leads" in data:
        leads = data["leads"]
    elif isinstance(data, dict) and "data" in data:
        leads = data["data"]
    elif isinstance(data, list):
        leads = data
    else:
        leads = []

    # -------------------------------------------------
    # OUTPUT UX
    # -------------------------------------------------
    if not leads:
        st.warning("No leads returned")
        st.json(data)
        st.stop()

    df = pd.DataFrame(leads)

    st.success(f"✅ {len(df)} leads generated")

    if keywords:
        st.info(f"🔑 Keywords used: {', '.join(keywords)}")

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
