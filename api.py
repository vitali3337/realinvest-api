import estate_parser

@app.get("/run-parser")
def run_parser_now():
    estate_parser.run()
    return {"status": "parser executed"}
