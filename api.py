from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json, os, uuid, httpx
from datetime import datetime

app = FastAPI()

DATA_FILE = "houses.json"
LEADS_FILE = "leads.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_leads():
    try:
        with open(LEADS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_leads(data):
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "HTML"}
            )
    except:
        pass

@app.get("/")
def root():
    data = load_data()
    return {"status": "ESTA API working", "listings": len(data)}

@app.get("/listings")
def get_listings(limit: int = 50, offset: int = 0):
    data = load_data()
    total = len(data)
    results = data[offset: offset + limit]
    return {"total": total, "offset": offset, "limit": limit, "listings": results}

@app.post("/listings")
async def add_listing(request: Request):
    new_item = await request.json()
    data = load_data()
    new_item["id"] = new_item.get("id") or str(uuid.uuid4())[:8]
    new_item["parsed"] = datetime.now().isoformat()
    new_item["views"] = 0
    new_item["is_vip"] = new_item.get("is_vip", False)
    new_item["source"] = new_item.get("source", "manual")
    data.append(new_item)
    save_data(data)
    return {"ok": True, "id": new_item["id"]}

@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: str):
    data = load_data()
    data = [d for d in data if d.get("id") != listing_id]
    save_data(data)
    return {"ok": True}

@app.post("/listings/{listing_id}/vip")
def make_vip(listing_id: str):
    data = load_data()
    for item in data:
        if item.get("id") == listing_id:
            item["is_vip"] = True
    save_data(data)
    return {"ok": True}

@app.post("/leads")
async def add_lead(request: Request):
    lead = await request.json()
    lead["id"] = str(uuid.uuid4())[:8]
    lead["created_at"] = datetime.now().isoformat()
    lead["status"] = "new"
    leads = load_leads()
    leads.insert(0, lead)
    save_leads(leads)
    # Telegram notification
    msg = (
        f"📥 <b>Новая заявка ESTA</b>\n"
        f"👤 {lead.get('name','—')} · {lead.get('phone','—')}\n"
        f"🏠 {lead.get('listing', lead.get('message','Общий вопрос'))}\n"
        f"📞 {lead.get('contact_via', lead.get('contact','Звонок'))} · {lead.get('contact_time', lead.get('time','Любое'))}"
    )
    await send_telegram(msg)
    return {"ok": True, "id": lead["id"]}

@app.get("/leads")
def get_leads(secret: str = ""):
    if secret != "realinvest2024":
        return {"error": "unauthorized"}
    return {"leads": load_leads()}

@app.patch("/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, request: Request):
    body = await request.json()
    leads = load_leads()
    for lead in leads:
        if lead.get("id") == lead_id:
            lead["status"] = body.get("status", "done")
    save_leads(leads)
    return {"ok": True}

@app.post("/parse")
async def run_parse(request: Request):
    try:
        import estate_parser
        estate_parser.run()
        return {"ok": True, "message": "Парсер запущен"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/run-parser")
def run_parser():
    try:
        import estate_parser
        estate_parser.run()
        return {"status": "parser executed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
        
