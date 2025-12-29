import streamlit as st
import requests
import pandas as pd
from sectors import SECTORS

st.set_page_config(page_title="LeadForge AI", page_icon="🚀", layout="wide")

st.title("🚀 LeadForge AI")
st.subheader("Multi-Sector Lead Generation Platform")
st.caption("Built for Apify 1M Challenge")

st.sidebar.header("Lead Configuration")
sector = st.sidebar.selectbox("Industry", list(SECTORS.keys()))
city = st.sidebar.text_input("Target City", "Chennai")

filters = {}
for f in SECTORS[sector]["filters"]:
    filters[f] = st.sidebar.text_input(f)

generate = st.sidebar.button("Generate Leads")

if generate:
    with st.spinner("Generating leads..."):
        payload = {"sector": sector,"city": city,"filters": filters}
        res = requests.post("http://localhost:8000/generate-leads", json=payload)
        data = res.json()
        df = pd.DataFrame(data["leads"])

    st.success(f"{data['count']} Leads Generated")
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False), "leads.csv", "text/csv")
else:
    st.info("Select industry & filters from sidebar to start")
