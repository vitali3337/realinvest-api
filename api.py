from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "RealInvest API"}

@app.get("/listings")
def listings():
    return [
        {"id":1,"title":"Дом центр","price":85000},
        {"id":2,"title":"Квартира Балка","price":42000}
    ]
