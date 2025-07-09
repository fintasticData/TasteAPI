import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
from pydantic import BaseModel
from datetime import datetime
#from API_Database import TransactionFilter, get_filtered_transactions, get_unique_values, get_recent_transactions
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from diffusers import StableDiffusionPipeline
import torch
import time
from google import genai
from google.genai import types
from google.oauth2 import service_account

app = FastAPI()
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
pipe = pipe.to("cuda")

@app.post("/generate-image")
async def generate_image(prompt: str):
    image = pipe(prompt).images[0]
    image.save("generated_image.png")
    return {"message": "Image generated successfully!"}


#import logging
# Setting up logging for debugging 
#logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SERVICE_ROLE_KEY = os.getenv("SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure Google Generative AI API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Generative AI model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

#OpenAIAPI
#client = OpenAI(api_key="your-api-key-here")
client = OpenAI(api_key=os.getenv("OPENAI"))
MODEL = "03-mini"


#Github
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = os.getenv("GITHUB_API_URL")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=   ["*"] ,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your frontend URL)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
async def root():
    return {"message": "My Taste"}



app = FastAPI()

class VideoRequest(BaseModel):
    prompt: str
    record_id: str

# Initialize credentials & client globally (or per request if needed)
creds = service_account.Credentials.from_service_account_file(
    "path/to/your/service_account.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = genai.Client(
    vertexai=True,
    project="fintastic-godrej",
    location="us-central1",
    credentials=creds,
)

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    try:
        operation = client.models.generate_videos(
            model="veo-3.0-fast-generate-preview",
            prompt=request.prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8
            ),
        )

        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        if operation.done and operation.response:
            videos = []
            for idx, generated_video in enumerate(operation.response.generated_videos):
                video_bytes = generated_video.video.video_bytes
                # You can upload to your storage here or return bytes/base64
                videos.append({
                    "filename": f"{request.record_id}_{idx}.mp4",
                    "video_bytes": video_bytes.hex()  # or base64 encode
                })
            return {"status": "success", "videos": videos}
        else:
            raise HTTPException(status_code=500, detail="Operation did not complete successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


