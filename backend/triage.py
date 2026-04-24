import requests
from functools import lru_cache
from langgraph.graph import StateGraph, START, END
from functools import lru_cache
import os
from google import genai

# 🔗 AI Service URL
# AI_URL = "http://ai-service:8001/generate"

# # Setup Gemini
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# gemini_model = genai.GenerativeModel("gemini-1.0-pro")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
@lru_cache(maxsize=100)
def call_ai(prompt: str):

    # 🔥 Gemini first
    try:
        print("Using Gemini")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip() if hasattr(response, "text") and response.text else ""

        if text:
            return text

    except Exception as e:
        print("Gemini failed:", e)

    # 🔥 Fallback → Ollama
    try:
        print("Using Ollama fallback")

        res = requests.post(
            "http://host.minikube.internal:11434/api/generate",
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        return res.json().get("response", "").strip()

    except Exception as e:
        print("Ollama failed:", e)
        return ""
    
# ---------------- NODE FUNCTIONS ---------------- #

# ⚡ FAST validation (no LLM)
def validate_symptom(state):
    text = state["symptom"].strip().lower()
    state["is_valid"] = len(text) >= 3
    return state


# ⚡ Classification (cached)
def classify_symptom(state):
    prompt = (
        f"You are a medical assistant. Classify the symptom: '{state['symptom']}' "
        "into one word: General, Emergency, or Mental Health."
    )
    output = call_ai(prompt)
    state["category"] = output.strip().lower()
    
    return state


def symptom_router(state):
    c = state["category"]
    if "general" in c:
        return "general"
    if "emergency" in c:
        return "emergency"
    if "mental" in c:
        return "mental_health"
    return "general"


def general_node(state):
    state["answer"] = f"'{state['symptom']}' seems general. We'll connect you to the General department."
    return state


def emergency_node(state):
    state["answer"] = f"'{state['symptom']}' seems to be an emergency! Please act fast."
    return state


def mental_health_node(state):
    state["answer"] = f"'{state['symptom']}' could be a mental health issue. Let's connect you to a counsellor."
    return state


def advice_node(state):
    cat = state["category"]
    state["advice"] = (
        "Please rest and monitor your symptoms." if "general" in cat else
        "Contact emergency services immediately." if "emergency" in cat else
        "Talk to someone you trust or a professional counsellor." if "mental" in cat else
        "Consult a doctor for detailed advice."
    )
    return state


# ⚡ PARALLEL execution (BIG SPEED BOOST)
def parallel_node(state):

    prompt = f"""
    For symptom '{state['symptom']}' in city '{state['city']}', provide:

    1. Diet suggestion (2-3 lines)
    2. Specialist doctor type
    3. 2 hospitals in that city

    Format:
    DIET: ...
    SPECIALIST: ...
    HOSPITALS: ...
    """

    output = call_ai(prompt)

    # basic parsing
    diet = ""
    follow = ""

    if "DIET:" in output and "SPECIALIST:" in output:
        diet = output.split("DIET:")[1].split("SPECIALIST:")[0].strip()

    if "SPECIALIST:" in output:
        follow = output.split("SPECIALIST:")[1].strip()

    return {
        **state,
        "diet": diet,
        "follow_up": follow
    }

# ---------------- GRAPH ---------------- #

builder = StateGraph(dict)

builder.add_node("validate", validate_symptom)
builder.add_node("classify", classify_symptom)
builder.add_node("general", general_node)
builder.add_node("emergency", emergency_node)
builder.add_node("mental_health", mental_health_node)
builder.add_node("advice", advice_node)
builder.add_node("parallel", parallel_node)

# Flow
builder.add_edge(START, "validate")

builder.add_conditional_edges(
    "validate",
    lambda s: "classify" if s["is_valid"] else "__end__",
    {
        "classify": "classify",
        "__end__": END
    }
)

builder.add_conditional_edges(
    "classify",
    symptom_router,
    {
        "general": "general",
        "emergency": "emergency",
        "mental_health": "mental_health"
    }
)

builder.add_edge("general", "advice")
builder.add_edge("emergency", "advice")
builder.add_edge("mental_health", "advice")

# ⚡ Parallel instead of sequential
builder.add_edge("advice", "parallel")
builder.add_edge("parallel", END)

graph = builder.compile()


# ---------------- ENTRY FUNCTION ---------------- #

def process_triage(data):
    state = {
        "symptom": data.get("symptom"),
        "city": data.get("city")
    }

    result = graph.invoke(state)
    return result