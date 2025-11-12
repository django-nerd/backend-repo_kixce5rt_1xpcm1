import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Portfolio, Project, SocialLink

app = FastAPI(title="Interactive Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Helpers ---------
class ObjectIdStr(BaseModel):
    id: str

def to_public(doc: dict):
    if not doc:
        return doc
    d = doc.copy()
    if isinstance(d.get("_id"), ObjectId):
        d["id"] = str(d.pop("_id"))
    return d

# --------- Public API ---------
@app.get("/")
def read_root():
    return {"message": "Interactive Portfolio API running"}

@app.get("/api/portfolio")
def get_portfolio():
    """Return the latest/only portfolio settings document."""
    if db is None:
        # Fallback default if DB not configured
        return {
            "hero_title": "Hey, I'm Alex — Creative Developer",
            "hero_subtitle": "I build playful, interactive web experiences.",
            "about": "I love crafting modern, interactive interfaces that feel alive.",
            "socials": [
                {"label": "GitHub", "url": "https://github.com/", "icon": "github"},
                {"label": "LinkedIn", "url": "https://linkedin.com/", "icon": "linkedin"}
            ],
        }
    doc = db["portfolio"].find_one({})
    if not doc:
        # Seed a default document
        seed = Portfolio().model_dump()
        create_document("portfolio", seed)
        doc = db["portfolio"].find_one({})
    return to_public(doc)

@app.get("/api/projects")
def list_projects():
    """List projects ordered by 'order' then featured first."""
    if db is None:
        # Sample when DB not available
        return [
            {
                "title": "Toybox UI",
                "description": "A playful component kit with physics.",
                "tags": ["react", "framer-motion"],
                "featured": True,
                "order": 1,
                "link": "https://example.com"
            },
            {
                "title": "3D Playground",
                "description": "WebGL experiments and microgames.",
                "tags": ["threejs", "spline"],
                "order": 2
            }
        ]
    items = list(db["project"].find({}).sort([("featured", -1), ("order", 1)]))
    return [to_public(x) for x in items]

# --------- Admin API ---------
class PortfolioUpdate(Portfolio):
    pass

class ProjectCreate(Project):
    pass

@app.post("/api/admin/portfolio")
def update_portfolio(payload: PortfolioUpdate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    doc = db["portfolio"].find_one({})
    data = payload.model_dump()
    if doc:
        db["portfolio"].update_one({"_id": doc["_id"]}, {"$set": data})
        return {"status": "updated"}
    else:
        create_document("portfolio", data)
        return {"status": "created"}

@app.post("/api/admin/projects")
def create_project(payload: ProjectCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    new_id = create_document("project", payload)
    return {"id": new_id}

@app.delete("/api/admin/projects/{project_id}")
def delete_project(project_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        oid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    res = db["project"].delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "deleted"}

# Simple health and schema endpoints
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
