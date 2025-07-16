from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from dotenv import load_dotenv
import os

from reddit_scraper import setup_reddit_praw_instance, get_username_from_url, scrape_user_data
from persona_builder import build_persona_with_llm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

app = FastAPI(
    title="Reddit Persona Builder API",
    description="API for scraping Reddit user data and building user personas using LLMs.",
    version="1.0.0"
)

reddit_praw_instance = None

@app.on_event("startup")
async def startup_event():
    global reddit_praw_instance
    try:
        reddit_praw_instance = setup_reddit_praw_instance()
    except Exception as e:
        logging.error(f"Failed to initialize Reddit PRAW instance on startup: {e}")

class PersonaRequest(BaseModel):
    url: str

class PersonaResponse(BaseModel):
    username: str
    persona_text: str

@app.post("/build_persona", response_model=PersonaResponse)
async def build_user_persona(request: PersonaRequest):
    if reddit_praw_instance is None:
        raise HTTPException(status_code=500, detail="Reddit PRAW instance not initialized. Check server logs.")
    user_profile_url = request.url
    logging.info(f"Request received to build persona for URL: {user_profile_url}")
     
    try:
        username = get_username_from_url(user_profile_url)

        scraped_data = scrape_user_data(reddit_praw_instance, username)

        if not scraped_data or (not scraped_data['comments'] and not scraped_data['posts']):
            raise HTTPException(status_code=404, detail=f"No sufficient data found for user /u/{username}.")
        
        persona_text = build_persona_with_llm(scraped_data)

        if not persona_text:
            raise HTTPException(status_code=500, detail="Failed to generate persona from LLM.")

        return PersonaResponse(username=username, persona_text=persona_text)
    
    except ValueError as ve:
        logging.error(f"Input validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"An unexpected error occurred during persona building: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
