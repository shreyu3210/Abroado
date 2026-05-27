import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas.chat import ChatRequest
from app.services.chat_service import generate_chat_response

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
    return await generate_chat_response(request)