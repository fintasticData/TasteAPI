import streamlit as st
import requests
import os
from supabase import create_client, Client

# Load environment variables
load_dotenv()


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

# Section 1: List Existing Repositories
st.header("Existing Repositories")
repos = fetch_repos()
if repos:
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

# Section 3: Manage Trending Styles
st.header("Trending Hair Braiding Styles")
styles = fetch_trending_styles()
if styles:
    st.write("List of trending styles:")
    for style in styles:
        st.write(f"- **{style['name']}**: {style['description']}")
else:
    st.write("No trending styles found.")
