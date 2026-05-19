import os
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware to allow requests from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can change this to specific domains later
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Input Schemas
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Load website info once at startup
WEBSITE_INFO_PATH = os.path.join(os.path.dirname(__file__), "web-info", "website_info.json")
try:
    with open(WEBSITE_INFO_PATH, "r", encoding="utf-8") as f:
        website_info = json.load(f)
except Exception as e:
    website_info = {"error": f"Could not load website info: {str(e)}"}
app.mount("/static", StaticFiles(directory="test_frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("test_frontend/index.html")

@app.get("/about")
def read_about():
    return {"message": "About Page"}

@app.get("/api/test")
def test_endpoint():
    return {"message": "Hello World!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key.strip() in ["", "your_api_key_here"]:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the backend .env file. Please add GEMINI_API_KEY to your .env file."
        )

    # System instruction guiding the model to use the website info
    system_prompt = (
        "You are a helpful AI assistant representing the website 'Abroado'. "
        "You answer user questions about Abroado based ONLY on the following website information:\n"
        f"{json.dumps(website_info, indent=2)}\n\n"
        "Instructions:\n"
        "1. Be friendly, professional, concise, and helpful.\n"
        "2. Only answer using the facts and details provided above. If the information is not in the website info, "
        "politely state that you don't know or ask them to contact support at info@abroado.com or call +91 123 456 7890.\n"
        "3. Do not invent any facts, links, services, or contact details not present in the provided JSON."
    )

    # Format the contents for Gemini native API
    contents = []
    for msg in request.messages:
        # Gemini expects 'model' instead of 'assistant'
        role = "model" if msg.role == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg.content}]
        })

    # Call Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)

            if response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Gemini API returned a '429 Too Many Requests' error. Please try again in a few seconds."
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Gemini API error: {response.text}"
                )

            res_data = response.json()
            
            try:
                bot_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                bot_text = "Sorry, I received an empty or invalid response from the model."

            # Return in OpenAI/OpenRouter compatible structure so frontend doesn't break
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": bot_text
                        }
                    }
                ]
            }

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while requesting Gemini API: {str(exc)}"
            )