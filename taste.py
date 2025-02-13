import streamlit as st
import requests
from pydantic import BaseModel
from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain.chains import RetrievalQA
from langchain.llms import GooglePalm
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Qdrant client
qdrant_client = QdrantClient(host="localhost", port=6333)  # Replace with your Qdrant server details

# Initialize embeddings (e.g., Hugging Face)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Qdrant as a LangChain vector store
collection_name = "recipes"
vector_store = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embeddings,
)

# Initialize LangChain RetrievalQA chain
llm = GooglePalm(google_api_key=os.getenv("GEMINI_API_KEY"))  # Replace with Gemini when supported
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(),
)

# Define the API base URL
API_BASE_URL = os.getenv("API_BASE_URL")  # Ensure you set this in your .env file

class Recipe(BaseModel):
    name: str
    description: str
    ingredients: list[str]
    instructions: str

class Query(BaseModel):
    query: str

# Function to add a recipe
def add_recipe(recipe: Recipe):
    response = requests.post(f"{API_BASE_URL}/add-recipe/", json=recipe.dict())
    if response.status_code != 200:
        raise Exception(f"Failed to add recipe: {response.text}")
    return response.json()

# Function to query recipes
def query_recipes(query: Query):
    response = requests.post(f"{API_BASE_URL}/query-recipes/", json=query.dict())
    if response.status_code != 200:
        raise Exception(f"Failed to query recipes: {response.text}")
    return response.json()

# Streamlit app
st.title("Recipe Chatbot")

# Input for adding a new recipe
with st.expander("Add a New Recipe"):
    name = st.text_input("Name")
    description = st.text_area("Description")
    ingredients = st.text_area("Ingredients (comma-separated)")
    instructions = st.text_area("Instructions")
    if st.button("Add Recipe"):
        if name and description and ingredients and instructions:
            recipe = Recipe(
                name=name,
                description=description,
                ingredients=ingredients.split(","),
                instructions=instructions
            )
            result = add_recipe(recipe)
            st.success(result["message"])
        else:
            st.error("Please fill in all fields.")

# Input for querying recipes
query_input = st.text_input("Ask about recipes:")
if st.button("Query"):
    if query_input:
        query = Query(query=query_input)
        result = query_recipes(query)
        st.write(result["response"])
    else:
        st.error("Please enter a query.")
