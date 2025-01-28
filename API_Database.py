from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import date

class TransactionFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    city: Optional[str] = None
    product: Optional[str] = None
    sales_rep: Optional[str] = None

class TransactionResponse(BaseModel):
    transactions: List[dict]
    summary: dict
    unique_values: dict

async def get_filtered_transactions(supabase, filters: TransactionFilter):
    # Get unique values for each column
    unique_cities = supabase.table('transactions').select('city').execute()
    unique_products = supabase.table('transactions').select('product').execute()
    unique_sales_reps = supabase.table('transactions').select('sales_rep').execute()
    
    unique_values = {
        'cities': sorted(list(set(row['city'] for row in unique_cities.data))),
        'products': sorted(list(set(row['product'] for row in unique_products.data))),
        'sales_reps': sorted(list(set(row['sales_rep'] for row in unique_sales_reps.data)))
    }

    # Build the query for filtered transactions
    query = supabase.table('transactions').select('*')
    
    if filters.start_date:
        query = query.gte('date', filters.start_date.isoformat())
    if filters.end_date:
        query = query.lte('date', filters.end_date.isoformat())
    if filters.city:
        query = query.eq('city', filters.city)
    if filters.product:
        query = query.eq('product', filters.product)
    if filters.sales_rep:
        query = query.eq('sales_rep', filters.sales_rep)
    
    try:
        response = query.execute()
        transactions = response.data
        
        # Calculate summary statistics
        if transactions:
            total_sales = sum(t['total'] for t in transactions)
            avg_price = sum(t['price'] for t in transactions) / len(transactions)
            total_quantity = sum(t['quantity'] for t in transactions)
        else:
            total_sales = 0
            avg_price = 0
            total_quantity = 0
            
        summary = {
            'total_sales': round(total_sales, 2),
            'avg_price': round(avg_price, 2),
            'total_quantity': total_quantity,
            'transaction_count': len(transactions)
        }
        
        return TransactionResponse(
            transactions=transactions,
            summary=summary,
            unique_values=unique_values
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
