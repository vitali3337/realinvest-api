"""
РеалИнвест — FastAPI Backend v3.0
Деплой: Railway
Документация: /docs (автоматически)

Переменные окружения (Railway → Variables):
  TELEGRAM_TOKEN   — токен бота
  TELEGRAM_CHAT    — ID группы/канала
  API_SECRET       — секрет для защищённых эндпоинтов (придумай сам)
  ANTHROPIC_API_KEY — ключ Claude API (для AI-поиска)
"""

from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json, os, hashlib, requests
from datetime import datetime

# ══════════════════════════════════════════
app = FastAPI(
    title="РеалИнвест API",
    description="API для портала недвижимости Тирасполя",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # для GitHub Pages — разрешаем всё
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE      = "houses.json"
LEADS_FILE     = "leads.json"
TG_TOKEN       = os.getenv("TELEGRAM_TOKEN", "")
TG_CHAT        = os.getenv("TELEGRAM_CHAT", "")
API_SECRET     = os.getenv("API_SECRET", "realinvest2024")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

# ── Pydantic схемы ──────────────────────────────────────────

class Listing(BaseModel):
    id:       Optional[str] = None
    title:    str
    type:     str = "дом"          # дом | квартира | участок | коммерция
    district: str = ""
    price:    int                  # USD
    area:     Optional[int] = None
    rooms:    Optional[int] = None
    floor:    Optional[str] = None
    img:      Optional[str] = None
    imgs:     Optional[List[str]] = []
    desc:     Optional[str] = None
    link:     Optional[str] = None
    source:   str = "manual"
    is_vip:   bool = False
    parsed:   Optional[str] = None

class Lead(BaseModel):
    name:    str
    phone:   str
    contact: str = "Звонок"
    time:    str = "Любое время"
    listing: Optional[str] = None
    comment: Optional[str] = None

# ── Утилиты ─────────────────────────────────────────────────

def load(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def make_id(title: str) -> str:
    return hashlib.md5((title + datetime.now().isoformat()).encode()).hexdigest()[:10]

def check_secret(x_secret: str = Header(default="")):
    if x_secret != API_SECRET:
        raise HTTPException(status_code=401, detail="Неверный API ключ")
    return True

def send_telegram(text: str):
    if not TG_TOKEN or not TG_CHAT:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": text, "parse_mode": "Markdown"},
            timeout=8,
        )
        return r.status_code == 200
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════
#  LISTINGS — объявления
# ═══════════════════════════════════════════════════════════

@app.get("/listings", summary="Список объявлений с фильтрами")
def get_listings(
    q:        Optional[str] = Query(None, description="Текстовый поиск"),
    type:     Optional[str] = Query(None, description="дом | квартира | участок | коммерция"),
    district: Optional[str] = Query(None, description="Район"),
    price_min: Optional[int] = Query(None, description="Цена от ($)"),
    price_max: Optional[int] = Query(None, description="Цена до ($)"),
    rooms:    Optional[int] = Query(None, description="Количество комнат"),
    sort:     str = Query("date_desc", description="date_desc | price_asc | price_desc | area_desc"),
    limit:    int = Query(50, le=200),
    offset:   int = Query(0),
):
    data = load(DATA_FILE)

    # Фильтрация
    if q:
        q_low = q.lower()
        data = [l for l in data if q_low in l.get("title","").lower()
                                 or q_low in l.get("district","").lower()
                                 or q_low in l.get("desc","").lower()]
    if type:
        data = [l for l in data if l.get("type") == type]
    if district:
        data = [l for l in data if district.lower() in l.get("district","").lower()]
    if price_min is not None:
        data = [l for l in data if l.get("price", 0) >= price_min]
    if price_max is not None:
        data = [l for l in data if l.get("price", 0) <= price_max]
    if rooms is not None:
        data = [l for l in data if l.get("rooms") == rooms]

    # Сортировка
    sort_map = {
        "price_asc":  lambda x: x.get("price", 0),
        "price_desc": lambda x: -x.get("price", 0),
        "area_desc":  lambda x: -(x.get("area") or 0),
        "date_desc":  lambda x: x.get("parsed", ""),
    }
    data.sort(key=sort_map.get(sort, sort_map["date_desc"]), reverse=(sort == "date_desc"))

    # VIP наверх
    data.sort(key=lambda x: 0 if x.get("is_vip") else 1)

    total = len(data)
    return {
        "total":    total,
        "offset":   offset,
        "limit":    limit,
        "listings": data[offset : offset + limit],
    }


@app.get("/listings/{listing_id}", summary="Один объект по ID")
def get_listing(listing_id: str):
    data = load(DATA_FILE)
    item = next((l for l in data if l.get("id") == listing_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Объект не найден")
    return item


@app.post("/listings", summary="Добавить объект (защищено)", dependencies=[Depends(check_secret)])
def add_listing(listing: Listing):
    data = load(DATA_FILE)
    obj = listing.dict()
    obj["id"]     = make_id(listing.title)
    obj["parsed"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data.insert(0, obj)
    save(DATA_FILE, data)
    return {"ok": True, "id": obj["id"]}


@app.delete("/listings/{listing_id}", summary="Удалить объект (защищено)", dependencies=[Depends(check_secret)])
def delete_listing(listing_id: str):
    data = load(DATA_FILE)
    new_data = [l for l in data if l.get("id") != listing_id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Не найден")
    save(DATA_FILE, new_data)
    return {"ok": True, "deleted": listing_id}


# ═══════════════════════════════════════════════════════════
#  LEADS — заявки
# ═══════════════════════════════════════════════════════════

@app.post("/leads", summary="Принять заявку с сайта")
def create_lead(lead: Lead):
    leads = load(LEADS_FILE)
    obj = lead.dict()
    obj["id"]   = make_id(lead.name + lead.phone)
    obj["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    leads.insert(0, obj)
    save(LEADS_FILE, leads)

    # Уведомление в Telegram
    msg = (
        f"🔔 *Новая заявка с сайта*\n\n"
        f"👤 {lead.name}\n"
        f"📞 {lead.phone}  |  {lead.contact}\n"
        f"🕐 Время: {lead.time}\n"
        f"🏡 Объект: {lead.listing or '—'}\n"
        f"💬 {lead.comment or '—'}\n\n"
        f"_РеалИнвест · {obj['date']}_"
    )
    send_telegram(msg)

    return {"ok": True, "id": obj["id"]}


@app.get("/leads", summary="Список заявок (защищено)", dependencies=[Depends(check_secret)])
def get_leads(limit: int = Query(50)):
    leads = load(LEADS_FILE)
    return {"total": len(leads), "leads": leads[:limit]}



# ═══════════════════════════════════════════════════════════
#  AI SEARCH — гибридный поиск через Claude
# ═══════════════════════════════════════════════════════════

class AiSearchRequest(BaseModel):
    query: str
    limit: int = 4

@app.post("/ai-search", summary="AI-поиск по базе объявлений")
def ai_search(req: AiSearchRequest):
    """
    Гибридный поиск: Claude разбирает запрос → применяем фильтры → ранжируем.
    Ключ Claude хранится на сервере — фронтенду не нужен.
    """
    if not ANTHROPIC_KEY:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY не задан в переменных Railway")

    listings = load(DATA_FILE)
    if not listings:
        return {"comment": "База объявлений пока пуста.", "matches": []}

    # Шаг 1: Claude извлекает структурированные фильтры из запроса
    extract_prompt = f"""Ты — парсер запросов недвижимости. Извлеки параметры из запроса пользователя.
Отвечай ТОЛЬКО валидным JSON без markdown, без пояснений.

Формат ответа:
{{
  "type": "дом|квартира|участок|коммерция|null",
  "district": "название района или null",
  "price_max": число в USD или null,
  "price_min": число в USD или null,
  "rooms_min": минимум комнат или null,
  "area_min": минимум площади м² или null,
  "keywords": ["ключевые слова для поиска"],
  "intent": "покупка|аренда|инвестиция|покупка"
}}

Районы Тирасполя: центр, балка, западный, хутор, суклея, кировское.
Если "семья" / "дети" — rooms_min: 3, area_min: 90.
Если "инвестиция" / "вложить" — сортируй по цене.
Если валюта рубли — конвертируй: 1$ ≈ 18 руб.

Запрос: "{req.query}"
"""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",   # быстрая и дешёвая модель для извлечения
                "max_tokens": 300,
                "messages": [{"role": "user", "content": extract_prompt}],
            },
            timeout=15,
        )
        raw = r.json()["content"][0]["text"].strip()
        filters = json.loads(raw.replace("```json","").replace("```","").strip())
    except Exception as e:
        # Если парсинг не удался — ищем по ключевым словам
        filters = {"keywords": [req.query]}

    # Шаг 2: Применяем фильтры к базе
    candidates = listings[:]

    if filters.get("type"):
        candidates = [l for l in candidates if l.get("type") == filters["type"]]
    if filters.get("district"):
        d = filters["district"].lower()
        candidates = [l for l in candidates if d in l.get("district","").lower()]
    if filters.get("price_max"):
        candidates = [l for l in candidates if l.get("price",0) <= filters["price_max"]]
    if filters.get("price_min"):
        candidates = [l for l in candidates if l.get("price",0) >= filters["price_min"]]
    if filters.get("rooms_min"):
        candidates = [l for l in candidates if (l.get("rooms") or 0) >= filters["rooms_min"]]
    if filters.get("area_min"):
        candidates = [l for l in candidates if (l.get("area") or 0) >= filters["area_min"]]

    # Если фильтры слишком жёсткие — берём все и даём Claude выбрать
    pool = candidates if candidates else listings
    pool = pool[:30]  # не перегружаем контекст

    # Шаг 3: Claude ранжирует и объясняет
    rank_prompt = f"""Ты — риэлтор-консультант агентства ESTA в Тирасполе. Помоги клиенту.

Запрос клиента: "{req.query}"

Доступные объекты (JSON):
{json.dumps(pool, ensure_ascii=False, indent=1)}

Выбери {min(req.limit, len(pool))} наиболее подходящих объектов и объясни выбор.

Отвечай ТОЛЬКО валидным JSON:
{{
  "comment": "Дружелюбный ответ клиенту 1-2 предложения — что нашёл и почему",
  "matches": [
    {{
      "id": "id объекта",
      "score": "high|mid|low",
      "reason": "Конкретная причина почему подходит клиенту (1 предложение)"
    }}
  ]
}}

Правила:
- score high = отлично совпадает с запросом
- score mid = хорошо, но есть нюансы  
- score low = частично подходит
- reason — конкретный, не общий ("цена $78к вписывается в бюджет $90к и район Суклея тихий")
- Если ничего не подходит — matches: [] и объясни в comment почему
"""

    try:
        r2 = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": rank_prompt}],
            },
            timeout=20,
        )
        raw2 = r2.json()["content"][0]["text"].strip()
        result = json.loads(raw2.replace("```json","").replace("```","").strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI ранжирования: {str(e)}")

    # Добавляем полные данные объектов в ответ
    listing_map = {l["id"]: l for l in listings if "id" in l}
    enriched_matches = []
    for m in result.get("matches", []):
        obj = listing_map.get(m["id"])
        if obj:
            enriched_matches.append({**m, "listing": obj})

    return {
        "comment":  result.get("comment", ""),
        "matches":  enriched_matches,
        "filters_applied": filters,
        "candidates_count": len(candidates),
    }


# ═══════════════════════════════════════════════════════════
#  STATS & HEALTH
# ═══════════════════════════════════════════════════════════

@app.get("/stats", summary="Статистика портала")
def get_stats():
    listings = load(DATA_FILE)
    leads    = load(LEADS_FILE)
    types = {}
    for l in listings:
        t = l.get("type", "другое")
        types[t] = types.get(t, 0) + 1
    return {
        "total_listings": len(listings),
        "total_leads":    len(leads),
        "vip_count":      sum(1 for l in listings if l.get("is_vip")),
        "by_type":        types,
        "last_updated":   listings[0].get("parsed") if listings else None,
    }

@app.get("/", summary="Health check")
def root():
    return {"status": "ok", "service": "РеалИнвест API v2.0", "docs": "/docs"}
    
