from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

DATA_FILE = "houses.json"

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

@app.get("/")
def root():
    return {"status": "RealInvest API working"}

@app.get("/listings")
def get_listings(limit: int = 50, offset: int = 0):
    data = load_data()
    total = len(data)
    results = data[offset: offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "listings": results
    }

@app.get("/run-parser")
def run_parser():
    try:
        import estate_parser
        estate_parser.run()
        return {"status": "parser executed"}
    except Exception as e:
        return {"status": "parser error", "error": str(e)}
from fastapi import Request

@app.post("/listings")
async def add_listing(request: Request):

    new_item = await request.json()

    data = load_data()

    data.append(new_item)

    save_data(data)

    return {"status": "added"}
from fastapi import Request

@app.post("/listings")
async def add_listing(request: Request):

    new_item = await request.json()

    data = load_data()

    data.append(new_item)

    save_data(data)

    return {"status": "added"}
