# D:\assignment\reddit-persona-app\app.py

import streamlit as st
import requests
import json
import logging
from dotenv import load_dotenv
import os

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# FastAPI backend URL (set in .env or default to localhost)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Streamlit Page Configuration
st.set_page_config(
    page_title="Reddit Persona Builder",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🤖 Reddit User Persona Builder")
st.markdown("Enter a Reddit user profile URL to generate their persona using AI.")

# Input from user
user_url = st.text_input(
    "Reddit User Profile URL",
    placeholder="e.g., https://www.reddit.com/user/kojied",
    help="Enter the full URL to the Reddit user's profile page"
)

if st.button("Build persona"):
    if not user_url:
        st.error("Please enter a Reddit user profile URL.")
    else:
        with st.spinner("Scraping Reddit data and generating persona... This might take a moment"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/build_persona",
                    json={"url": user_url},
                    timeout=300
                )
                response.raise_for_status()

                persona_data = response.json()
                username = persona_data.get("username", "Unknown User")
                persona_text = persona_data.get("persona_text", "Could not retrieve persona text.")

                st.success(f"Persona for /u/{username} generated successfully!")
                st.subheader(f"Persona for /u/{username}")
                st.markdown(persona_text)

                st.download_button(
                    label="Download persona as Text",
                    data=persona_text,
                    file_name=f"{username}_persona.txt",
                    mime="text/plain"
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the backend API: {e}. Please ensure the FastAPI server is running.")
                logging.error(f"Streamlit: Request to backend failed: {e}")
            except json.JSONDecodeError:
                st.error("Failed to decode JSON response from backend. Server might have responded with invalid data.")
                logging.error(f"Streamlit: JSON decode error: {response.text}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.error("Streamlit: Unexpected error", exc_info=True)

st.markdown("---")
st.info("⚠️ Make sure the FastAPI backend is running before using this app: `uvicorn main:app --reload`")
