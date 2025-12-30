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
    print("🔥 /generate-leads called")
    print("📥 Request:", req.dict())

    try:
        print("🚀 Triggering Apify actor...")

        run = client.actor("sree_brag/multi-sector-lead-generator-actor").call(
            run_input=req.dict(),
            timeout_secs=120
        )

        print("✅ Actor finished")
        print("📦 Run info:", run)

        dataset_id = run.get("defaultDatasetId")
        items = client.dataset(dataset_id).list_items().items

        return {"count": len(items), "leads": items}

    except Exception as e:
        print("❌ BACKEND ERROR:", repr(e))
        return {
            "count": 0,
            "leads": [],
            "error": str(e)
        }
