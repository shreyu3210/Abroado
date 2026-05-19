from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow requests from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can change this to specific domains later
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/about")
def read_about():
    return {"message": "About Page"}

@app.get("/api/test")
def test_endpoint():
    return {"message": "Hello World!"}