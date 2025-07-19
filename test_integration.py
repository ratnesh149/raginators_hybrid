#!/usr/bin/env python3
"""
Test script for the Agentic HR Assistant Web Integration
This script tests the key components without starting the full web server
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test Flask imports
        import flask
        import flask_cors
        print("✅ Flask and CORS imported successfully")
        
        # Test vector database
        from services.vector_db import HRVectorDB, get_vector_db
        print("✅ Vector database service imported successfully")
        
        # Test candidate shortlist tool
        from tools.candidate_shortlist import candidate_shortlist_tool
        print("✅ Candidate shortlist tool imported successfully")
        
        # Test graph
        from graph.stategraph import graph
        print("✅ LangGraph imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_vector_db():
    """Test vector database functionality"""
    print("\n🔍 Testing vector database...")
    
    try:
        from services.vector_db import get_vector_db
        
        # Initialize vector database
        vector_db = get_vector_db()
        print("✅ Vector database initialized")
        
        # Add sample data
        vector_db.add_sample_data()
        print("✅ Sample data added")
        
        # Test search
        results = vector_db.search_candidates("React JavaScript", n_results=2)
        print(f"✅ Found {len(results)} candidates for React JavaScript")
        
        if results:
            print(f"   - First candidate: {results[0].get('metadata', {}).get('candidate_name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database error: {e}")
        return False

def test_candidate_tool():
    """Test candidate shortlisting tool"""
    print("\n🔍 Testing candidate shortlisting tool...")
    
    try:
        from tools.candidate_shortlist import candidate_shortlist_tool
        
        # Test the tool
        result = candidate_shortlist_tool._run(
            job_requirements="React JavaScript frontend developer",
            min_experience=3,
            n_candidates=3
        )
        
        print("✅ Candidate shortlisting tool executed successfully")
        print(f"   Result preview: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Candidate tool error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def test_file_structure():
    """Test that required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "web_app.py",
        "start_web_app.py",
        "jobDescription/hr_assistant.html",
        "jobDescription/index.html",
        "services/vector_db.py",
        "tools/candidate_shortlist.py",
        "graph/stategraph.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run all tests"""
    print("🧠 Agentic HR Assistant - Integration Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Vector Database", test_vector_db),
        ("Candidate Tool", test_candidate_tool)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your integration is ready.")
        print("Run: python start_web_app.py")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
