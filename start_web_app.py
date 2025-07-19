#!/usr/bin/env python3
"""
Startup script for the Agentic HR Assistant Web Application
This script initializes the system and starts the Flask web server
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        from services.vector_db import HRVectorDB, get_vector_db
        from graph.stategraph import graph
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def initialize_vector_db():
    """Initialize the vector database with sample data"""
    try:
        print("🔄 Initializing vector database...")
        from services.vector_db import get_vector_db
        vector_db = get_vector_db()
        vector_db.add_sample_data()
        print("✅ Vector database initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize vector database: {e}")
        print("The system will still work, but with limited candidate data")
        return False

def check_environment():
    """Check if environment variables are set"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def start_web_server():
    """Start the Flask web server"""
    try:
        print("🚀 Starting Agentic HR Assistant Web Server...")
        print("📍 Server will be available at: http://localhost:5000")
        print("🧠 HR Assistant interface: http://localhost:5000/hr_assistant.html")
        print("📋 Main interface: http://localhost:5000")
        print("\n" + "="*60)
        print("Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        # Import and run the web app
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🧠 Agentic HR Assistant - Web Application Startup")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize vector database
    initialize_vector_db()
    
    # Start web server
    start_web_server()

if __name__ == "__main__":
    main()
