print("***** LOADING GEMINI PERSONA_BUILDER *****")
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_persona_with_llm(user_data: dict) -> str:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        logging.error("GOOGLE_API_KEY not set in .env file")
        raise ValueError("Google API Key missing. Please set GOOGLE_API_KEY in your .env file.")

    genai.configure(api_key=api_key)

    username = user_data["username"]

    comments_text = "\n".join([
        f"Comment ({c['id']}) in r/{c['subreddit']}: {c['body']} [link: {c['permalink']}]"
        for c in user_data["comments"]
    ])

    posts_text = "\n".join([
        f"Post ({p['id']}) in r/{p['subreddit']}: Title: {p['title']} Body: {p['selftext']} [Link: {p['permalink']}]"
        for p in user_data["posts"]
    ])

    prompt_template = f"""
You are an expert user persona generator. Your task is to analyze the provided Reddit comments and posts of a user and create a detailed user persona.

The persona should include:
- **Basic Info**: Age, Occupation
- **Personality Traits**
- **Motivations**
- **Goals & Needs**
- **Frustrations**
- **Quote** summarizing their mindset.

Cite the specific Reddit comment/post ID and permalink that supports each insight.

Here’s the Reddit data for user /u/{username}:

--- Comments ---
{comments_text}

--- Posts ---
{posts_text}
"""

    logging.info(f"Sending persona prompt to Gemini for user /u/{username}")

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt_template)
        persona_text = response.text

        logging.info("Persona generated successfully by Gemini.")
        return persona_text
    except Exception as e:
        logging.error(f"Error generating persona from Gemini: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    pass
