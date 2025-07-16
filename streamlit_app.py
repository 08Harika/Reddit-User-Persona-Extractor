import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Your other imports
from reddit_scraper import setup_reddit_praw_instance, get_username_from_url, scrape_user_data
from persona_builder import build_persona_with_llm
import google.generativeai as genai

# Configure Gemini API from .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    st.error("Google API key not found. Please add it to your .env file as GOOGLE_API_KEY.")
    st.stop()
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Streamlit page title
st.title("Reddit Persona Builder")

# Text input for Reddit URL
reddit_url = st.text_input("Enter Reddit user profile URL:", value="https://www.reddit.com/user/kojied")

# Button to trigger persona building
if st.button("Build Persona"):
    if reddit_url:
        try:
            st.info("Scraping Reddit data...")

            reddit = setup_reddit_praw_instance()
            username = get_username_from_url(reddit_url)
            user_data = scrape_user_data(reddit, username)

            st.success(f"Scraped data for user: {username}")

            st.info("Sending data to Gemini to build persona...")

            persona_text = build_persona_with_llm(user_data)

            st.subheader("Persona for /u/" + username)
            st.write(persona_text)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a Reddit user URL.")
