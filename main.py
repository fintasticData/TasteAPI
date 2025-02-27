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

#import logging
# Setting up logging for debuggin
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

# fastapi_app.py
from fastapi import FastAPI


@app.get("/ping")
async def ping():
    return {"status": "up and running"}

# Define request body model


class GenerateTextRequest(BaseModel):
    question: str
    specific_note: str | None = None
    user_id: int
    project_id: int
    response_group_id: int

@app.post("/aimia")
async def generate_text_endpoint(request: GenerateTextRequest):
    """Endpoint to generate text and save the prompt and response to Supabase."""
    try:
        # Generate content using the AI model
        response = model.generate_content(request.question)  # AI model call

        # Ensure response is properly formatted as a string
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Prepare data for Supabase insertion
        data = {
            "response_id": str(uuid.uuid4()),
            "item_1": request.question,
            "item_2": request.specific_note,
            "response_text": response_text,
            "user_id": request.user_id,
            "project_id": request.project_id,
            "response_group_id": request.response_group_id,
            "response_date": datetime.now().isoformat()
        }

        # Insert data into Supabase table
        response = supabase.table("selection_responses").insert(data).execute()

        # Return success message
        return {"message": "Text generated and saved successfully", "generated_text": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/products")
async def get_all_products():
    """Fetch all products from the Supabase 'products' table."""
    try:
        response = supabase.table("products").select("*").execute()
        if response.data:  # Check if data is returned
            return response.data
        else:  # Handle empty results or errors
            raise HTTPException(status_code=500, detail="Error fetching products or no products found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Fetch a single product by ID from the Supabase 'products' table."""
    try:
        response = supabase.table("products").select("*").eq("id", product_id).single().execute()
        if response.data:  # Check if the product exists
            return response.data
        else:  # Handle product not found
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-text")
async def generate_text(prompt: str):
    """Generate text using the Google Generative AI model."""
    try:
        # Generate content using the AI model
        response = model.generate_content(prompt)
        if response.text:  # Check if the response contains text
            return {"generated_text": response.text}
        else:  # Handle cases where no text is generated
            raise HTTPException(status_code=500, detail="No text generated by the AI model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


supabase2: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# Define a Pydantic model to receive the SQL code
class SQLRequest(BaseModel):
    sql: str

# Endpoint to create a function in Supabase
@app.post("/create-function")
async def create_function(request: SQLRequest):
    try:
        # Extract the SQL code from the request
        sql_code = request.sql
        
        # Execute the SQL code to create the function in Supabase
        response = supabase2.postgrest.rpc("execute_sql", {"sql": sql_code})
        
        # If the response status is not 200, raise an exception
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error creating function")
        
        return {"message": "Function created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
