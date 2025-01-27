import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from typing import Optional
# FastAPI CORS setup
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-react-fps9i4n6s-aksharjs-projects.vercel.app/"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

