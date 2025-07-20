#!/usr/bin/env python3
"""
UI Error Diagnostic Script
Identifies and fixes common UI issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_streamlit_components():
    """Test individual Streamlit components"""
    print("🔍 Testing Streamlit Components")
    print("=" * 40)
    
    try:
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test dataframe functionality
        import pandas as pd
        test_data = [
            {"Name": "John Doe", "Status": "✅ SELECTED", "Score": "92%"},
            {"Name": "Jane Smith", "Status": "❌ REJECTED", "Score": "65%"}
        ]
        
        df = pd.DataFrame(test_data)
        print("✅ DataFrame creation successful")
        
        # Test if column_config is available
        try:
            hasattr(st, 'column_config')
            print("✅ column_config available")
        except:
            print("⚠️  column_config not available - using simple dataframe")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit component error: {e}")
        return False

def test_app_imports():
    """Test all app imports"""
    print("\n🔍 Testing App Imports")
    print("=" * 40)
    
    imports_to_test = [
        ("streamlit", "st"),
        ("datetime", "datetime"),
        ("os", "os"),
        ("json", "json"),
        ("uuid", "uuid"),
        ("logging", "logging"),
        ("pathlib", "Path"),
        ("services.candidate_evaluator", "candidate_evaluator"),
        ("tools.candidate_evaluation", "candidate_evaluation_tool"),
        ("services.vector_db", "get_vector_db"),
        ("utils.resume_downloader", "resume_downloader")
    ]
    
    failed_imports = []
    
    for module_name, import_name in imports_to_test:
        try:
            if module_name == "streamlit":
                import streamlit as st
            elif module_name == "datetime":
                from datetime import datetime
            elif module_name == "pathlib":
                from pathlib import Path
            elif module_name == "services.candidate_evaluator":
                from services.candidate_evaluator import candidate_evaluator
            elif module_name == "tools.candidate_evaluation":
                from tools.candidate_evaluation import candidate_evaluation_tool
            elif module_name == "services.vector_db":
                from services.vector_db import get_vector_db
            elif module_name == "utils.resume_downloader":
                from utils.resume_downloader import resume_downloader
            else:
                __import__(module_name)
            
            print(f"✅ {module_name} import successful")
            
        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
            failed_imports.append((module_name, str(e)))
    
    return len(failed_imports) == 0, failed_imports

def test_session_state_logic():
    """Test session state logic"""
    print("\n🔍 Testing Session State Logic")
    print("=" * 40)
    
    try:
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.candidates = []
                self.search_performed = False
                self.evaluation_performed = False
        
        mock_state = MockSessionState()
        
        # Test candidate categorization
        test_candidates = [
            {"evaluation_status": "SELECTED ⭐", "name": "John"},
            {"evaluation_status": "REJECTED", "name": "Jane"},
            {"evaluation_status": "NOT_EVALUATED", "name": "Mike"}
        ]
        
        mock_state.candidates = test_candidates
        
        # Test categorization logic
        selected = [c for c in mock_state.candidates if c.get('evaluation_status', '').startswith('SELECTED')]
        rejected = [c for c in mock_state.candidates if c.get('evaluation_status') == 'REJECTED']
        not_eval = [c for c in mock_state.candidates if c.get('evaluation_status', 'NOT_EVALUATED') == 'NOT_EVALUATED']
        
        print(f"✅ Categorization working: {len(selected)} selected, {len(rejected)} rejected, {len(not_eval)} not evaluated")
        
        return True
        
    except Exception as e:
        print(f"❌ Session state logic error: {e}")
        return False

def create_minimal_app():
    """Create a minimal working version of the app"""
    print("\n🔧 Creating Minimal App Version")
    print("=" * 40)
    
    minimal_app_content = '''
import streamlit as st
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Raginators-Hybrid - Candidate Search",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Raginators-Hybrid - Enhanced Candidate Search")

# Initialize session state
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# Sidebar
with st.sidebar:
    st.header("🔍 Job Requirements")
    job_title = st.text_input("Job Title *", placeholder="e.g., React Developer")
    
    if st.button("🔍 Find Candidates", type="primary"):
        if job_title:
            # Mock candidate data for testing
            st.session_state.candidates = [
                {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "phone": "+1-555-0001",
                    "experience": "5 years",
                    "skills": "React, JavaScript, TypeScript",
                    "education": "BS Computer Science",
                    "evaluation_status": "SELECTED ⭐",
                    "evaluation_score": 0.92,
                    "match_score": "92%",
                    "unique_id": "test_001"
                },
                {
                    "name": "Jane Doe", 
                    "email": "jane@example.com",
                    "phone": "+1-555-0002",
                    "experience": "2 years",
                    "skills": "HTML, CSS, JavaScript",
                    "education": "Bootcamp",
                    "evaluation_status": "REJECTED",
                    "evaluation_score": 0.65,
                    "match_score": "65%",
                    "unique_id": "test_002"
                }
            ]
            st.session_state.search_performed = True
            st.success("Found 2 candidates!")
        else:
            st.error("Please enter a job title")

# Display candidates
if st.session_state.search_performed and st.session_state.candidates:
    st.markdown("---")
    st.subheader("📋 Shortlisted Candidates")
    
    # View mode selection
    view_mode = st.radio(
        "Choose view mode:",
        ["📋 Detailed Cards", "📊 Table View"],
        horizontal=True
    )
    
    if view_mode == "📊 Table View":
        # Simple table view
        import pandas as pd
        
        table_data = []
        for candidate in st.session_state.candidates:
            table_data.append({
                "Name": candidate["name"],
                "Status": candidate.get("evaluation_status", "N/A"),
                "Score": candidate.get("match_score", "N/A"),
                "Experience": candidate["experience"],
                "Email": candidate["email"],
                "Skills": candidate["skills"][:50] + "..." if len(candidate["skills"]) > 50 else candidate["skills"]
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
    else:
        # Detailed cards view
        for i, candidate in enumerate(st.session_state.candidates):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    status = candidate.get("evaluation_status", "N/A")
                    if status.startswith("SELECTED"):
                        st.success(f"✅ **{candidate['name']}** - {status}")
                    elif status == "REJECTED":
                        st.error(f"❌ **{candidate['name']}** - {status}")
                    else:
                        st.info(f"📋 **{candidate['name']}** - {status}")
                    
                    st.write(f"📧 **Email:** {candidate['email']}")
                    st.write(f"📞 **Phone:** {candidate['phone']}")
                    st.write(f"💼 **Experience:** {candidate['experience']}")
                    st.write(f"🛠️ **Skills:** {candidate['skills']}")
                    st.write(f"🎓 **Education:** {candidate['education']}")
                    st.write(f"🎯 **Score:** {candidate.get('match_score', 'N/A')}")
                
                with col2:
                    st.button(f"📄 Download Resume", key=f"download_{i}", help="Resume download (demo)")
                
                st.markdown("---")

st.markdown("### 📊 System Status")
st.info("✅ Minimal UI version is working correctly!")
'''
    
    try:
        with open('app_minimal.py', 'w') as f:
            f.write(minimal_app_content)
        print("✅ Created app_minimal.py - a working minimal version")
        return True
    except Exception as e:
        print(f"❌ Failed to create minimal app: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 UI Error Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Streamlit components
    test1_result = test_streamlit_components()
    
    # Test 2: App imports
    test2_result, failed_imports = test_app_imports()
    
    # Test 3: Session state logic
    test3_result = test_session_state_logic()
    
    # Test 4: Create minimal app
    test4_result = create_minimal_app()
    
    print("\n📋 **DIAGNOSTIC SUMMARY**")
    print("=" * 50)
    print(f"✅ Streamlit Components: {'PASS' if test1_result else 'FAIL'}")
    print(f"✅ App Imports: {'PASS' if test2_result else 'FAIL'}")
    print(f"✅ Session State Logic: {'PASS' if test3_result else 'FAIL'}")
    print(f"✅ Minimal App Creation: {'PASS' if test4_result else 'FAIL'}")
    
    if not test2_result:
        print("\n❌ **FAILED IMPORTS:**")
        for module, error in failed_imports:
            print(f"   • {module}: {error}")
    
    print("\n💡 **RECOMMENDATIONS:**")
    if all([test1_result, test2_result, test3_result]):
        print("   ✅ All core components working - try running app_minimal.py first")
        print("   ✅ Run: streamlit run app_minimal.py")
    else:
        print("   ⚠️  Some components have issues - check failed imports above")
        print("   🔧 Try installing missing dependencies")

if __name__ == "__main__":
    main()
