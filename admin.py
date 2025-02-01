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


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()


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
tab1, tab2, tab3 = st.tabs(["Repositories", "Trending Styles", "Agent Tasks"])

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
