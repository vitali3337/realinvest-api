@app.get("/run-parser")
def run_parser():

    try:
        estate_parser.run()
        return {"status": "parser executed"}

    except Exception as e:
        return {
            "status": "parser error",
            "error": str(e)
        }
