# 🤖 TriageAI

TriageAI is an AI-powered symptom router that quickly classifies user symptoms into **General**, **Emergency**, or **Mental Health** — then gives tailored medical advice, diet suggestions, and city-specific doctors & hospitals.

Originally inspired by the **IBM SkillsBuild Masterclass**, I extended it to feel closer to a real-world hospital triage assistant.

-----------------------------------------------------
**Features**

✅ Symptom classification: General, Emergency, Mental Health  
✅ Dynamic diet suggestions (powered by Gemini)  
✅ Localized list of doctors & hospitals by city/state  
✅ Clean Streamlit UI  
✅ Disclaimer to keep it safe & responsible

--------------------------------------------------------

⚕️ **Why “TriageAI”?**  
In medical terms, **triage** means quickly assessing and categorizing patient symptoms to decide next steps — just like this app does.

--------------------------------------------------------

## 🛠 **Tech Stack**
- Python
- Streamlit
- LangGraph
- LangChain
- Gemini 1.5 Flash API

--------------------------------------------------------

## ⚙️ **Setup & Run Locally**

# 1️⃣ Clone the repo
git clone https://github.com/yourusername/TriageAI.git
cd TriageAI

# 2️⃣ Create and activate virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Set your Gemini API key (use a .env file or export directly)
echo "GOOGLE_API_KEY=your-api-key-here" > .env

# 5️⃣ Run the app
streamlit run triage_app.py
