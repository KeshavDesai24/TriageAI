# triage_app.py
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import streamlit as st

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not set in .env file")
os.environ['GOOGLE_API_KEY'] = api_key

# ✅ Initialize Gemini
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", temperature=0.4)

# --- Node functions ---
def classify_symptom(state: dict) -> dict:
    prompt = (
        f"You are a medical assistant. Classify the symptom: '{state['symptom']}' "
        "into one word: General, Emergency, or Mental Health."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    state["category"] = response.content.strip().lower()
    print(f"Classified as: {state['category']}")
    return state

def symptom_router(state: dict) -> str:
    c = state["category"]
    if "general" in c: return "general"
    if "emergency" in c: return "emergency"
    if "mental" in c: return "mental_health"
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

def diet_node(state):
    prompt = (
        f"As a certified dietitian, suggest a short diet tip for: '{state['symptom']}'. "
        "Start with: Diet Suggestion:"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    state["diet"] = response.content.strip()
    return state

def follow_up_node(state):
    prompt = (
        f"You are a hospital assistant AI.\n"
        f"Symptom: '{state['symptom']}'\n"
        f"City: '{state['city']}'\n"
        "Suggest:\n"
        "- Type of specialist doctor needed\n"
        "- 2–3 well-known hospitals in this city with specialization\n"
        "Return in markdown format like:\n"
        "### Specialist\nCardiologist\n\n### Hospitals\n- Lilavati Hospital, Bandra – Cardiology\n- Kokilaben Hospital, Andheri – Emergency Cardiac Care\n"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    state["follow_up"] = response.content.strip()
    return state

# --- Build LangGraph ---
builder = StateGraph(dict)
builder.add_node("classify", classify_symptom)
builder.add_node("general", general_node)
builder.add_node("emergency", emergency_node)
builder.add_node("mental_health", mental_health_node)
builder.add_node("advice", advice_node)
builder.add_node("diet", diet_node)
builder.add_node("follow_up", follow_up_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", symptom_router, {
    "general": "general",
    "emergency": "emergency",
    "mental_health": "mental_health"
})
builder.add_edge("general", "advice")
builder.add_edge("emergency", "advice")
builder.add_edge("mental_health", "advice")
builder.add_edge("advice", "diet")
builder.add_edge("diet", "follow_up")
builder.add_edge("follow_up", END)

graph = builder.compile()

# --- Streamlit UI ---
st.title("🤖 TriageAI: Symptom Router")

symptom = st.text_input("Enter your symptom:")
city = st.text_input("Enter your city/state:", "Mumbai")  # default to Mumbai

if st.button("Submit"):
    if symptom.strip() and city.strip():
        state = {"symptom": symptom, "city": city}
        result = graph.invoke(state)

        st.subheader("Diagnosis")
        st.write(result["answer"])

        st.subheader("Advice")
        st.write(result["advice"])

        st.subheader("Diet Suggestion")
        st.write(result["diet"])

        st.subheader("Recommended Doctors & Hospitals")
        with st.expander("Show details"):
            st.markdown(result["follow_up"])

        st.subheader("Next action")
        choice = st.radio("What would you like to do next?", [
            "Speak to doctor", "See hospitals", "Exit"
        ])
        if choice == "Speak to doctor":
            st.success("Connecting you to a doctor now...")
        elif choice == "See hospitals":
            st.info("Here are the hospitals recommended above.")
        else:
            st.write("Thank you! Wishing you good health. 🙏")
        st.caption("⚠️ *Disclaimer: This is an AI-generated demo. Please verify all medical information with certified professionals before use.*")
    else:
        st.warning("Please enter both symptom and city.")
        
