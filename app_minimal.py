
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
