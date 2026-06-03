import os
import json
import logging
import httpx
from fastapi import HTTPException
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

# Load website info once at startup
WEBSITE_INFO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web-info", "website_info.json")
try:
    with open(WEBSITE_INFO_PATH, "r", encoding="utf-8") as f:
        website_info = json.load(f)
except Exception as e:
    website_info = {"error": f"Could not load website info: {str(e)}"}

async def generate_chat_response(request: ChatRequest) -> dict:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key.strip() in ["", "your_api_key_here"]:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the backend .env file. Please add GEMINI_API_KEY to your .env file."
        )

    # System instruction guiding the model to use the website info
    system_prompt = (
      f"""
You are Abroado's AI assistant.

You help users with questions related to Abroado's services, study visas, visitor visas, IELTS preparation, destinations, contact information, and website navigation.

Website Information:
{json.dumps(website_info, indent=2)}

Guidelines:

1. Be friendly, professional, concise, and conversational.

2. Use ONLY the provided website information as your knowledge source.
However, you may intelligently infer or summarize information when the user's wording is different but semantically related.

Example:
- If users ask for the company's motto, vision, mission, or goal,
  you may derive it from the company description or main purpose.

3. Never invent:
- countries
- services
- fees
- visa guarantees
- office addresses
- contact details
- policies
- links

4. If information is genuinely unavailable,
politely say so and direct users to:
Email: info@abroado.in
Phone: +91 7778832033

5. If users ask where to find something on the website,
use the navigation links provided.

6. Keep responses short and natural.
Avoid sounding robotic or overly repetitive.

7. Do NOT say phrases like:
- "based on the provided information"
- "according to the data"
- "the details I have"

Speak naturally as a company assistant.
"""
      )

    # Format the contents for Gemini native API
    contents = []
    for msg in request.messages:
        # Gemini expects 'model' instead of 'assistant'
        role = "model" if msg.role == "assistant" else "user"
        
        text_content = msg.content if isinstance(msg.content, str) else json.dumps(msg.content)
        
        contents.append({
            "role": role,
            "parts": [{"text": text_content}]
        })

    # Formulate schema for JSON response
    response_schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Your response message to the user."
            },
            "links": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The text to display for the link"},
                        "url": {"type": "string", "description": "The URL of the link"}
                    },
                    "required": ["title", "url"]
                },
                "description": "Any relevant links from the website information to provide."
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Suggested follow-up questions. Maximum 2 suggestions."
            }
        },
        "required": ["text", "links", "suggestions"]
    }

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }


    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]
    max_retries = 3
    last_exception = None

    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            model_name = models[attempt % len(models)]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            
            try:
                response = await client.post(url, json=payload, timeout=30.0)

                if response.status_code == 429:
                    logger.warning(f"Attempt {attempt + 1} failed for model {model_name} with status 429. Retrying...")
                    last_exception = HTTPException(
                        status_code=429,
                        detail="Gemini API returned a '429 Too Many Requests' error. Please try again in a few seconds."
                    )
                    continue

                if response.status_code != 200:
                    logger.warning(f"Attempt {attempt + 1} failed for model {model_name} with status {response.status_code}. Retrying...")
                    last_exception = HTTPException(
                        status_code=response.status_code,
                        detail=f"Gemini API error: {response.text}"
                    )
                    continue

                logger.info(f"Successfully generated response using model: {model_name}")

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
                logger.warning(f"Attempt {attempt + 1} failed for model {model_name} with RequestError: {str(exc)}. Retrying...")
                last_exception = HTTPException(
                    status_code=500,
                    detail=f"An error occurred while requesting Gemini API: {str(exc)}"
                )
                continue

        if last_exception:
            logger.error("All retry attempts failed.")
            raise last_exception
