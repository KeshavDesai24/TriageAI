from fastapi import FastAPI
import requests

app = FastAPI()

# OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
# OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_URL = "http://host.minikube.internal:11434/api/generate"

@app.post("/generate")
def generate(data: dict):
    prompt = data.get("prompt")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        return {"response": response.json().get("response", "")}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}