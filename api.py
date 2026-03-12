from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json, os, uuid
from datetime import datetime

app = FastAPI()
DATA_FILE = "houses.json"
LEADS_FILE = "leads.json"

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load(f):
    try:
        with open(f, encoding="utf-8") as fp: return json.load(fp)
    except: return []

def save(f, d):
    with open(f, "w", encoding="utf-8") as fp: json.dump(d, fp, ensure_ascii=False, indent=2)

@app.get("/")
def root(): return {"status": "ok", "listings": len(load(DATA_FILE))}

@app.get("/listings")
def get_listings(limit: int = 200, offset: int = 0):
    d = load(DATA_FILE)
    return {"total": len(d), "offset": offset, "limit": limit, "listings": d[offset:offset+limit]}

@app.post("/listings")
async def add_listing(r: Request):
    item = await r.json()
    d = load(DATA_FILE)
    item["id"] = item.get("id") or str(uuid.uuid4())[:8]
    item["parsed"] = datetime.now().isoformat()
    item["is_vip"] = item.get("is_vip", False)
    item["source"] = item.get("source", "manual")
    d.append(item)
    save(DATA_FILE, d)
    return {"ok": True, "id": item["id"]}

@app.delete("/listings/{lid}")
def del_listing(lid: str):
    d = [x for x in load(DATA_FILE) if x.get("id") != lid]
    save(DATA_FILE, d)
    return {"ok": True}

@app.post("/listings/{lid}/vip")
def make_vip(lid: str):
    d = load(DATA_FILE)
    for x in d:
        if x.get("id") == lid: x["is_vip"] = True
    save(DATA_FILE, d)
    return {"ok": True}

@app.post("/leads")
async def add_lead(r: Request):
    lead = await r.json()
    lead["id"] = str(uuid.uuid4())[:8]
    lead["created_at"] = datetime.now().isoformat()
    lead["status"] = "new"
    leads = load(LEADS_FILE)
    leads.insert(0, lead)
    save(LEADS_FILE, leads)
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT", "")
    if token and chat:
        try:
            import httpx
            async with httpx.AsyncClient() as c:
                await c.post(f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat, "text": f"📥 Заявка ESTA\n👤 {lead.get('name','?')} {lead.get('phone','')}\n🏠 {lead.get('listing','')}"})
        except: pass
    return {"ok": True}

@app.get("/leads")
def get_leads(secret: str = ""):
    if secret != "realinvest2024": return {"error": "unauthorized"}
    return {"leads": load(LEADS_FILE)}
