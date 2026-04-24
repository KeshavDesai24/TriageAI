from fastapi import FastAPI
from triage import process_triage

app = FastAPI()

@app.post("/triage")
def triage(data : dict):
    result = process_triage(data)
    return result

