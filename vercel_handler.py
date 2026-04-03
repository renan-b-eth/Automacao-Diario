"""
Vercel Entry Point for Automação Diária
This file handles the serverless function for Vercel
"""
import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# Vercel serverless function handler
def handler(environ, start_response):
    return app(environ, start_response)