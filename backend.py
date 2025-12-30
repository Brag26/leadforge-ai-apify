from fastapi import FastAPI
from pydantic import BaseModel
from apify_client import ApifyClient
import os

app = FastAPI()

client = ApifyClient(os.environ.get("APIFY_API_TOKEN"))

class LeadRequest(BaseModel):
    sector: str
    city: str
    keyword: str | None = None
    maxResults: int = 10

@app.post("/generate-leads")
def generate_leads(req: LeadRequest):
    run = client.actor(
        "Brag26/multi-sector-lead-generator"
    ).call(run_input={
        "sector": req.sector,
        "city": req.city,
        "keyword": req.keyword,
        "maxResults": req.maxResults
    })

    dataset_id = run["defaultDatasetId"]
    items = client.dataset(dataset_id).list_items().items

    return {
        "count": len(items),
        "leads": items
    }
