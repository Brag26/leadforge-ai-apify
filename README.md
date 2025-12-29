# 🚀 LeadForge AI – Multi-Sector Lead Generation Tool

LeadForge AI is a Python-based lead generation platform built for the Apify 1M Challenge.

## Features
- Multi-sector lead generation
- Dynamic filters per industry
- Lead scoring
- CSV export
- Apify-ready backend
- Clean high-end UI

## Run Locally

pip install -r requirements.txt
uvicorn backend:app --reload
streamlit run app.py

## Apify Integration
This project is designed to integrate Apify Actors for real-world lead scraping.
Actor logic can be plugged into backend.py using ApifyClient.

License: MIT
