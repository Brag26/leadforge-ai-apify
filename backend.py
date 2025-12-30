from fastapi import FastAPI
from pydantic import BaseModel
from apify_client import ApifyClient
import os

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(
    title="LeadForge Backend",
    version="0.1.0",
    description="Backend API for LeadForge AI using Apify Actors"
)

# -------------------------------------------------
# Apify client (token must be in env)
# -------------------------------------------------
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_API_TOKEN environment variable not set")

client = ApifyClient(APIFY_TOKEN)

# -------------------------------------------------
# Request schema (matches Swagger + Streamlit)
# -------------------------------------------------
class LeadRequest(BaseModel):
    sector: str
    city: str
    keyword: str | None = ""
    postcode: str | None = ""
    country: str | None = "Australia"
    maxResults: int = 10

# -------------------------------------------------
# Health check (optional but useful)
# -------------------------------------------------
@app.get("/")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# Main endpoint
# -------------------------------------------------
@app.post("/generate-leads")
def generate_leads(req: LeadRequest):
    """
    Triggers the Apify actor and returns extracted leads.
    Always returns JSON.
    """
    try:
        # Call Apify Actor
        run = client.actor(
            "Brag26/multi-sector-lead-generator"
        ).call(
            run_input={
                "sector": req.sector,
                "city": req.city,
                "keyword": req.keyword,
                "postcode": req.postcode,
                "country": req.country,
                "maxResults": req.maxResults,
            }
        )

        # Fetch dataset results
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return {
                "count": 0,
                "leads": [],
                "error": "Actor did not return a dataset ID"
            }

        items = client.dataset(dataset_id).list_items().items

        return {
            "count": len(items),
            "leads": items
        }

    except Exception as e:
        # Never crash the frontend
        return {
            "count": 0,
            "leads": [],
            "error": str(e)
        }
