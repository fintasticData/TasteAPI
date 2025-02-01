import streamlit as st
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
from API_Database import TransactionFilter, get_filtered_transactions, get_unique_values, get_recent_transactions
import requests
from bs4 import BeautifulSoup
import openai



# Load environment variables
load_dotenv(".env")

# Initialize FastAPI app
app = FastAPI()
openai.api_key = os.getenv("OPENAI")

# Replace these with your actual URLs and credentials
FASTAPI_URL = "https://tasteapi.onrender.com"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Function to fetch repositories from FastAPI
def fetch_repos():
    response = requests.get(f"{FASTAPI_URL}/list-repos/")
    if response.status_code == 200:
        return response.json().get("repositories", [])
    else:
        st.error("Failed to fetch repositories.")
        return []

# Function to create a new repository via FastAPI
def create_repo(repo_name, description, private):
    repo_data = {
        "repo_name": repo_name,
        "description": description,
        "private": private
    }
    response = requests.post(f"{FASTAPI_URL}/create-repo/", json=repo_data)
    if response.status_code == 200:
        st.success("Repository created successfully!")
    else:
        st.error(f"Failed to create repository: {response.json()}")

# Function to fetch trending styles from Supabase
def fetch_trending_styles():
    # Replace this with your actual Supabase client setup
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('trending_styles').select('*').execute()
    return response.data

# Streamlit App
st.title("GitHub Repository Admin Panel")

# Create Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Repositories", "Trending Styles", "Agent Tasks", "Testing", "Supabase Test", "OPenAI"])

# Tab 1: Repositories
with tab1:
    st.header("Manage Repositories")

    # Section 1: List Existing Repositories
    repos = fetch_repos()

    
    if repos:
        with st.expander("View Existing Repositories", expanded=False):
            st.write("List of repositories:")
            for repo in repos:
                st.write(f"- {repo}")
    else:
        st.write("No repositories found.")

    # Section 2: Create a New Repository
    st.header("Create a New Repository")
    with st.form("create_repo_form"):
        repo_name = st.text_input("Repository Name")
        description = st.text_input("Description")
        private = st.checkbox("Private Repository")
        submitted = st.form_submit_button("Create Repository")
        if submitted:
            if repo_name:
                create_repo(repo_name, description, private)
            else:
                st.error("Repository name is required.")

# Tab 2: Trending Styles
with tab2:
    st.header("Manage Trending Styles")

    # Fetch and Display Trending Styles
    styles = fetch_trending_styles()
    if styles:
        with st.expander("View Trending Styles", expanded=False):
            st.write("List of trending styles:")
            for style in styles:
                st.write(f"- **{style['name']}**: {style['description']}")
    else:
        st.write("No trending styles found.")

# Tab 3: Agent Tasks
with tab3:
    st.header("Assign Tasks to the Agent")

    # Example Task Assignment Form
    with st.form("assign_task_form"):
        task_name = st.text_input("Task Name")
        task_description = st.text_area("Task Description")
        assign_to = st.selectbox("Assign To", ["Agent A", "Agent B", "Agent C"])
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Assign Task")
        if submitted:
            if task_name and task_description:
                st.success(f"Task '{task_name}' assigned to {assign_to} with due date {due_date}.")
            else:
                st.error("Task name and description are required.")

# Tab 4: Testing
    with tab4:
        st.header("Assign Tasks to the Agent")
    
        # GitHub Repositories
        if st.button("Fetch GitHub Repos"):
            response = requests.get(f"{FASTAPI_URL}/list-repos")
            if response.status_code == 200:
                repos = response.json().get("repositories", [])
                st.write("Your GitHub Repositories:")
                st.write(repos)
            else:
                st.error("Failed to fetch GitHub repositories")
        
        # Ask OpenAI
        prompt = st.text_input("Ask OpenAI:")
        if st.button("Ask"):
            response = requests.post(f"{FASTAPI_URL}/ask", json={"prompt": prompt})
            if response.status_code == 200:
                answer = response.json()["response"]
                st.write("OpenAI Response:")
                st.write(answer)
            else:
                st.error("Failed to get response from OpenAI")
        
        # Store Data in Supabase
        data_to_store = st.text_input("Enter data to store in Supabase (JSON format):")
        if st.button("Store Data"):
            try:
                data = eval(data_to_store)  # Convert string to dict (be cautious with eval)
                response = requests.post(f"{FASTAPI_URL}/store_data", json=data)
                if response.status_code == 200:
                    st.success("Data stored successfully!")
                else:
                    st.error("Failed to store data in Supabase")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab5:
        # Form for creating a new table
        with st.form("create_table_form"):
            st.subheader("Create a New Table in Supabase")
            
            table_name = st.text_input("Table Name", placeholder="Enter table name")
            schema = st.text_area("Schema", placeholder="Enter schema (e.g., name TEXT, age INTEGER)")
            
            submitted = st.form_submit_button("Create Table")
            
            if submitted:
                if not table_name or not schema:
                    st.error("Please provide both table name and schema.")
                else:
                    # Send request to FastAPI backend
                    response = requests.post(f"{FASTAPI_URL}/create-table", json={
                        "table_name": table_name,
                        "schema": schema
                    })
                    
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error(f"Failed to create table: {response.json().get('detail', 'Unknown error')}")
    with tab6:
        def get_openai_response(prompt):
            client = openai.Client(api_key=os.getenv("OPENAI"))
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error: {e}"
        
        # Streamlit UI
        st.title("Test OpenAI API with Streamlit")
        
        with st.form(key='api_form'):
            prompt = st.text_area("Enter your prompt:", "Say hello!")
            submit_button = st.form_submit_button("Submit")
            
        if submit_button:
            if not os.getenv("OPENAI"):
                st.error("Missing OpenAI API Key. Set it in the environment variables.")
            else:
                response = get_openai_response(prompt)
                st.subheader("API Response:")
                st.write(response)
