import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LeadForge AI", layout="wide")

st.title("🚀 LeadForge AI")
st.caption("Powered by Apify Actors + AI")

# Sidebar
st.sidebar.header("Lead Search")

sector = st.sidebar.selectbox(
    "Sector",
    ["Healthcare", "Real Estate", "Manufacturing", "IT", "Education"]
)
city = st.sidebar.text_input("City", "Chennai")
keyword = st.sidebar.text_input("Keyword", "")
postcode = st.sidebar.text_input("Postcode (optional)", "")
country = st.sidebar.text_input("Country", "Australia")
max_results = st.sidebar.slider("Max Results", 1, 20, 10)

if st.sidebar.button("Generate Leads"):
    with st.spinner("Running Apify Actor…"):
        response = requests.post(
            "http://localhost:8000/generate-leads",
            json={
                "sector": sector,
                "city": city,
                "keyword": keyword,
                "postcode": postcode,
                "country": country,
                "maxResults": max_results,
            },
            timeout=300,
        )

if response.status_code != 200:
    st.error(f"Backend error {response.status_code}")
    st.code(response.text)
    st.stop()

try:
    data = response.json()
except Exception:
    st.error("Backend did not return JSON")
    st.code(response.text)
    st.stop()
    leads = data.get("leads", [])

    if not leads:
        st.warning("No leads found.")
    else:
        df = pd.DataFrame(leads)

        # Reorder columns nicely
        preferred_order = [
            "name",
            "category",
            "phone",
            "website",
            "rating",
            "reviewCount",
            "address",
            "googleMapsUrl",
            "searchQuery",
        ]

        df = df[[c for c in preferred_order if c in df.columns]]

        st.success(f"✅ {len(df)} leads found")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "leads.csv",
            "text/csv",
        )
