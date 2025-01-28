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
from API_Database import TransactionFilter, get_filtered_transactions

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure Google Generative AI API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Generative AI model
model = genai.GenerativeModel('gemini-pro')

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

# Define the new route for average price by type
@app.get("/analytics/average-price-by-type")
async def get_average_price_by_type():
    """Fetch the average price of products grouped by type."""
    try:
        response = supabase.rpc("get_average_price_by_type").execute()
        if response.data:
            return response.data
        else:
            raise HTTPException(status_code=500, detail="Error fetching average prices or no data found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all data from the transactions table
@app.get("/transactions")
async def get_all_transactions():
    """Fetch all transactions from the Supabase 'transactions' table."""
    try:
        response = supabase.table("transactions").select("*").execute()
        if response.data:  # Check if the table contains data
            return response.data
        else:  # Handle empty table
            raise HTTPException(status_code=404, detail="No transactions found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Fetch the analytics pack from the Supabase database."""
    try:
        # Call the function get_analytics_pack() which returns the precomputed analytics
        response = supabase.rpc("get_analytics_pack").execute()
        
        if response.data:  # Check if data is returned
            return response.data
        else:  # Handle empty results or errors
            raise HTTPException(status_code=500, detail="Error fetching analytics data.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateTextRequest(BaseModel):
    prompt: str
    user_id: str
    category: str
    sub_category: str
    retailer_name: str
    location: str

@app.post("/generate-text2")
async def generate_text_endpoint(request: GenerateTextRequest):
    """Endpoint to generate text and save the prompt and response to Supabase."""
    try:
        # Generate content using the AI model
        response = model.generate_content(request.prompt)
        if response.text:  # Check if the response contains text
            generated_text = response.text

            # Prepare data for Supabase insertion
            data = {
                "id": str(uuid.uuid4()),  # Generate a unique UUID
                "category": request.category,
                "sub_category": request.sub_category,
                "prompt": request.prompt,
                "response": generated_text,
                "model_name": "Google Generative AI",  # Replace with your actual model name
                "created_at": datetime.now().isoformat(),
                "user_id": request.user_id,
                "retailer_name": request.retailer_name,
                "location": request.location
            }

            # Insert data into the Supabase table
            supabase.table("gpt_responses").insert(data).execute()

            return {"generated_text": generated_text}
        else:  # Handle cases where no text is generated
            raise HTTPException(status_code=500, detail="No text generated by the AI model.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Supabase endpont for getting transactions
@app.post("/api/transactions")
async def filter_transactions(filters: TransactionFilter):
    return await get_filtered_transactions(supabase, filters)


@app.get("/api/unique-values")
async def get_unique_values_endpoint():
    """Fetch all unique values for filtering from the transactions table."""
    return await get_unique_values(supabase)

#Get LAtest 20 transactions
@app.get("/api/recent-transactions")
async def get_recent_transactions_endpoint(limit: Optional[int] = 20):
    """Fetch the most recent transactions, defaulting to 20."""
    if limit > 100:  # Add a reasonable upper limit
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100 transactions")
    return await get_recent_transactions(supabase, limit)
