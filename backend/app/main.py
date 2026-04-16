# Ezer Backend - main.py
# This is the entry point of the Ezer backend server

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# This is how Ezer reads your API key safely
load_dotenv("backend/.env")

# Create the FastAPI application
app = FastAPI(
    title="Ezer API",
    description="AI-powered insurance escalation engine for policyholders",
    version="1.0.0"
)

# This is the root endpoint
# When someone visits the backend URL, they see this message
@app.get("/")
def read_root():
    return {
        "product": "Ezer",
        "tagline": "With you through denial.",
        "status": "alive",
        "version": "1.0.0"
    }

# Health check endpoint
# Used to confirm the server is running
@app.get("/health")
def health_check():
    return {"status": "healthy"}