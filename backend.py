from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI(title="LeadForge AI Backend")

class LeadRequest(BaseModel):
    sector: str
    city: str
    filters: dict

@app.post("/generate-leads")
def generate_leads(request: LeadRequest):
    leads = []
    for i in range(10):
        leads.append({
            "Name": f"Lead {i+1}",
            "Phone": f"+91 9{random.randint(100000000,999999999)}",
            "Email": f"lead{i+1}@example.com",
            "City": request.city,
            "Sector": request.sector,
            "Score": random.randint(65, 95)
        })
    return {"status": "success","count": len(leads),"leads": leads}
