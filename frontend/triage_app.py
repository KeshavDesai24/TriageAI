import streamlit as st # type: ignore
import requests

# ---------------- UI ----------------
st.set_page_config(page_title="TriageAI", page_icon="🤖")

st.title("🤖 TriageAI: Symptom Router")

symptom = st.text_input("Enter your symptom:")
city = st.text_input("Enter your city/state:")

if st.button("Submit"):

    if not symptom or not city:
        st.warning("Please enter both symptom and city.")
    
    else:
        try:
            # 🔥 Call Backend API
            res = requests.post(
                "http://backend:8000/triage",   # Docker service name
                json={
                    "symptom": symptom,
                    "city": city
                }
            )

            data = res.json()

            # ---------------- OUTPUT ----------------
            if not data.get("is_valid", True):
                st.error("Invalid symptom. Please try again.")
            
            else:
                st.subheader("Diagnosis")
                st.write(data.get("answer", "No diagnosis available"))

                st.subheader("Advice")
                st.write(data.get("advice", "No advice available"))

                st.subheader("Diet Suggestion")
                st.write(data.get("diet", "No diet suggestion available"))

                st.subheader("Recommended Doctors & Hospitals")
                st.markdown(data.get("follow_up", "No recommendations available"))

                # ---------------- NEXT ACTION ----------------
                st.subheader("Next Action")

                option = st.radio(
                    "What would you like to do next?",
                    ["Speak to doctor", "See hospitals", "Exit"]
                )

                if option == "Speak to doctor":
                    st.success("Connecting you to a doctor now...")

                elif option == "See hospitals":
                    st.info("Scroll up to view recommended hospitals.")

                elif option == "Exit":
                    st.warning("Session ended. Stay safe!")

                # ---------------- DISCLAIMER ----------------
                st.caption("⚠️ This is an AI-generated demo. Please verify medical information with professionals.")

        except Exception as e:
            st.error(f"Error connecting to backend: {e}")