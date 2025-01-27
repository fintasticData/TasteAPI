import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from typing import Optional

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    return {"message": "My Taste"}

@app.get("/products")
async def get_all_products():
    """Fetch all products from the Supabase 'products' table."""
    try:
        response = supabase.table("products").select("*").execute()
        if response.error:
            raise HTTPException(status_code=500, detail=response.error.message)
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Fetch a single product by ID from the Supabase 'products' table."""
    try:
        response = supabase.table("products").select("*").eq("id", product_id).single().execute()
        if response.error:
            raise HTTPException(status_code=404, detail=response.error.message)
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
