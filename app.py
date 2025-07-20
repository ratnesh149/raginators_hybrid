import streamlit as st
from graph.stategraph import graph
import json
import uuid
import logging
import os
import zipfile
import tempfile
from pathlib import Path
import base64
from datetime import datetime
from utils.resume_downloader import resume_downloader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for minimalistic design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-weight: 300;
        margin-bottom: 2rem;
    }
    .chat-container {
        height: 600px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        background-color: #fafafa;
    }
    .selection-panel {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    .candidate-card {
        background-color: white;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .candidate-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .candidate-name {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .candidate-info {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin: 0.2rem 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: none;
        background-color: #3498db;
        color: white;
        font-weight: 500;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    .download-stats {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .metric-card {
        background-color: white;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Resume Selector",
    page_icon="📋",
    layout="wide"
)

st.markdown('<h1 class="main-header">Resume Selection Assistant</h1>', unsafe_allow_html=True)

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm here to help you find the right candidates. Use the selection panel to specify your requirements."
    })

if "candidates" not in st.session_state:
    st.session_state.candidates = []

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

if "search_timestamp" not in st.session_state:
    st.session_state.search_timestamp = None

# Create two columns - Chat on left, Selection panel on right
col1, col2 = st.columns([1, 1])

# Left Column - Chat Interface
with col1:
    st.subheader("💬 Chat Assistant")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about the selection process...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process through graph
        try:
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            graph_input = {"messages": [("user", user_input)]}
            
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response_content = ""
                    
                    for step in graph.stream(graph_input, config=config):
                        for node_name, node_response in step.items():
                            if node_name in ["chatbot", "jd_agent", "checklist_agent", "candidate_agent"]:
                                if "messages" in node_response:
                                    messages = node_response.get("messages", "")
                                    
                                    if isinstance(messages, str):
                                        content = messages
                                    elif isinstance(messages, list):
                                        content = " ".join([msg if isinstance(msg, str) else str(msg) for msg in messages])
                                    else:
                                        content = str(messages)
                                    
                                    if content.startswith("Chatbot needs clarification: "):
                                        content = content[len("Chatbot needs clarification: "):]
                                    
                                    if content.strip():
                                        response_content = content
                                        break
                    
                    if response_content:
                        st.write(response_content)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_content
                        })
                    else:
                        error_msg = "I couldn't process your request. Please try again."
                        st.write(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        
        except Exception as e:
            error_msg = "An error occurred. Please try again."
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Right Column - Selection Panel
with col2:
    st.subheader("🎯 Resume Selection")
    
    with st.container():
        st.markdown('<div class="selection-panel">', unsafe_allow_html=True)
        
        # Job Title
        job_title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
        
        # Required Skills
        required_skills = st.text_area("Required Skills", 
                                     placeholder="e.g., Python, React, AWS\n(one per line or comma-separated)",
                                     height=80)
        
        # Experience Level
        experience_level = st.selectbox("Experience Level", 
                                      ["Any", "Entry Level (0-2 years)", "Mid Level (3-5 years)", 
                                       "Senior Level (6-10 years)", "Expert Level (10+ years)"])
        
        # Location
        location = st.text_input("Preferred Location", placeholder="e.g., Remote, New York, etc.")
        
        # Education
        education = st.selectbox("Education Level", 
                               ["Any", "High School", "Bachelor's", "Master's", "PhD"])
        
        # Number of candidates
        num_candidates = st.slider("Number of Candidates", min_value=1, max_value=20, value=5)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Search button
        if st.button("🔍 Find Candidates", type="primary"):
            if job_title:
                # Set search timestamp
                st.session_state.search_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Generate enhanced query based on form inputs
                query_parts = []
                
                # Add job title with variations
                if job_title:
                    query_parts.append(f"Job Title: {job_title}")
                    # Add common variations
                    if "software engineer" in job_title.lower():
                        query_parts.append("Software Developer Frontend Developer Full Stack Developer")
                
                # Enhanced skills processing
                if required_skills:
                    skills_list = [skill.strip() for skill in required_skills.replace('\n', ',').split(',') if skill.strip()]
                    query_parts.append(f"Required Skills: {', '.join(skills_list)}")
                    
                    # Add skill context for better matching
                    skill_context = []
                    for skill in skills_list:
                        skill_lower = skill.lower()
                        if skill_lower == 'react':
                            skill_context.extend(['React.js', 'ReactJS', 'Frontend', 'JavaScript', 'JSX', 'Component'])
                        elif skill_lower == 'javascript':
                            skill_context.extend(['JS', 'ECMAScript', 'Frontend', 'Web Development'])
                        elif skill_lower == 'python':
                            skill_context.extend(['Django', 'Flask', 'Backend', 'Data Science'])
                    
                    if skill_context:
                        query_parts.append(f"Related Technologies: {', '.join(skill_context[:10])}")
                
                if experience_level != "Any":
                    query_parts.append(f"Experience: {experience_level}")
                
                if location:
                    query_parts.append(f"Location: {location}")
                
                if education != "Any":
                    query_parts.append(f"Education: {education}")
                
                query_parts.append(f"Number of candidates needed: {num_candidates}")
                
                generated_query = "\n".join(query_parts)
                
                # Add to chat
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Find candidates based on these requirements:\n{generated_query}"
                })
                
                # Process through actual vector database
                try:
                    from tools.candidate_shortlist import CandidateShortlistTool
                    
                    with st.spinner("Searching candidates in vector database..."):
                        # Initialize the candidate shortlist tool
                        shortlist_tool = CandidateShortlistTool()
                        
                        # Extract experience requirement (both min and max)
                        min_exp = 0
                        max_exp = 999  # Default to no upper limit
                        
                        if experience_level != "Any":
                            if "0-2" in experience_level:
                                min_exp, max_exp = 0, 2
                            elif "3-5" in experience_level:
                                min_exp, max_exp = 3, 5
                            elif "6-10" in experience_level:
                                min_exp, max_exp = 6, 10
                            elif "10+" in experience_level:
                                min_exp, max_exp = 10, 999
                        
                        # Run the actual candidate shortlisting
                        result = shortlist_tool._run(
                            job_requirements=generated_query,
                            min_experience=min_exp,
                            max_experience=max_exp,
                            n_candidates=num_candidates
                        )
                        
                        # Parse the result to extract candidate information
                        if "No candidates found" in result:
                            st.session_state.candidates = []
                            st.session_state.search_performed = False
                            st.warning("No candidates found matching your criteria.")
                        else:
                            # Use the already filtered and processed results from shortlist tool
                            # Get the filtered results that respect experience requirements
                            from services.vector_db import get_vector_db
                            vector_db = get_vector_db()
                            
                            # Get raw results and apply the same filtering logic as the shortlist tool
                            raw_results = vector_db.search_candidates(generated_query, num_candidates * 3)
                            
                            # Apply experience filtering (same logic as shortlist tool)
                            filtered_results = []
                            for candidate in raw_results:
                                metadata = candidate.get('metadata', {})
                                candidate_experience = metadata.get('experience_years', 0)
                                
                                # Apply the same experience filter as the shortlist tool
                                if min_exp <= candidate_experience <= max_exp:
                                    filtered_results.append(candidate)
                            
                            # Process and deduplicate the filtered results
                            unique_results = shortlist_tool._deduplicate_candidates(filtered_results)
                            
                            # Convert to display format
                            candidates_list = []
                            for i, candidate in enumerate(unique_results[:num_candidates]):
                                metadata = candidate.get('metadata', {})
                                
                                # Calculate match score based on distance (improved calculation)
                                distance = candidate.get('distance', 1.0)
                                # ChromaDB uses cosine distance, normalize it better
                                if distance <= 1.0:
                                    match_score = max(0, min(100, int((1 - distance) * 100)))
                                else:
                                    # For distances > 1, use exponential decay
                                    match_score = max(0, min(100, int(100 * (2 - distance))))
                                
                                # Ensure minimum score for actual matches
                                if distance < 1.5:  # Reasonable similarity threshold
                                    match_score = max(match_score, 10)  # Minimum 10% for reasonable matches
                                
                                candidate_info = {
                                    "name": metadata.get('candidate_name', 'Unknown'),
                                    "email": metadata.get('email', 'Not provided'),
                                    "phone": metadata.get('phone', 'Not provided'),
                                    "experience": f"{metadata.get('experience_years', 0)} years",
                                    "skills": metadata.get('skills', 'Not specified'),
                                    "location": metadata.get('location', 'Not specified'),
                                    "education": metadata.get('education', 'Not specified'),
                                    "match_score": f"{match_score}%",
                                    "unique_id": metadata.get('unique_id', f'candidate_{i}'),
                                    "pdf_file_path": metadata.get('pdf_file_path', ''),
                                    "pdf_filename": metadata.get('pdf_filename', '')
                                }
                                candidates_list.append(candidate_info)
                            
                            st.session_state.candidates = candidates_list
                            st.session_state.search_performed = True
                        
                        # Add experience filter info to the success message
                        exp_filter_msg = ""
                        if experience_level != "Any":
                            if max_exp == 999:
                                exp_filter_msg = f" (filtered for {min_exp}+ years experience)"
                            else:
                                exp_filter_msg = f" (filtered for {min_exp}-{max_exp} years experience)"
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Found {len(st.session_state.candidates)} unique candidates from the vector database matching your criteria{exp_filter_msg}. All candidates are guaranteed to be unique through our hybrid deduplication system!"
                        })
                        
                except Exception as e:
                    st.error(f"Error during candidate search: {str(e)}")
                    logger.error(f"Candidate search error: {e}")
                    st.session_state.candidates = []
                    st.session_state.search_performed = False
            else:
                st.warning("Please enter a job title to search for candidates.")

# Display candidates if search was performed
if st.session_state.search_performed and st.session_state.candidates:
    st.markdown("---")
    st.subheader("📋 Shortlisted Candidates from Vector Database")
    
    # Show experience filter info if applied
    if 'experience_level' in locals() and experience_level != "Any":
        if experience_level == "Entry Level (0-2 years)":
            exp_range = "0-2 years"
        elif experience_level == "Mid Level (3-5 years)":
            exp_range = "3-5 years"
        elif experience_level == "Senior Level (6-10 years)":
            exp_range = "6-10 years"
        elif experience_level == "Expert Level (10+ years)":
            exp_range = "10+ years"
        else:
            exp_range = experience_level
            
        st.info(f"✅ **Deduplication Guarantee**: All {len(st.session_state.candidates)} candidates are 100% unique using hybrid deduplication system\n\n🎯 **Experience Filter Applied**: Only showing candidates with {exp_range} experience")
    else:
        st.info(f"✅ **Deduplication Guarantee**: All {len(st.session_state.candidates)} candidates are 100% unique using hybrid deduplication system")
    
    # Get download statistics
    download_stats = resume_downloader.get_download_stats(st.session_state.candidates)
    
    # Display download statistics and bulk download
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        if st.button("📦 Download All Resumes (ZIP)", type="secondary"):
            with st.spinner("Creating ZIP file with all resumes..."):
                zip_path = resume_downloader.create_bulk_download_zip(st.session_state.candidates)
                if zip_path:
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download ZIP File",
                            data=f.read(),
                            file_name=f"shortlisted_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            key="bulk_download"
                        )
                    # Clean up temp file
                    try:
                        os.remove(zip_path)
                        os.rmdir(os.path.dirname(zip_path))
                    except:
                        pass
                    st.success(f"✅ ZIP file created with {download_stats['available_resumes']} resumes!")
                else:
                    st.error("❌ Failed to create ZIP file")
    
    with col2:
        # CSV download button
        csv_content = resume_downloader.create_candidates_csv(st.session_state.candidates)
        if csv_content:
            st.download_button(
                label="📊 Download CSV",
                data=csv_content,
                file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="csv_download",
                help="Download candidate information as spreadsheet"
            )
    
    with col3:
        st.metric("Total Candidates", download_stats['total_candidates'])
    
    with col4:
        st.metric("Available Resumes", f"{download_stats['available_resumes']}")
    
    with col5:
        st.metric("Availability Rate", f"{download_stats['availability_rate']:.1f}%")
    
    # Show missing resumes warning if any
    if download_stats['missing_resumes']:
        with st.expander(f"⚠️ {len(download_stats['missing_resumes'])} Resume(s) Not Found", expanded=False):
            st.write("The following candidates' resume files could not be located:")
            for name in download_stats['missing_resumes']:
                st.write(f"• {name}")
    
    st.markdown("---")
    
    # Display individual candidates with download buttons
    for i, candidate in enumerate(st.session_state.candidates):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Determine match quality for styling
            match_score_num = int(candidate['match_score'].replace('%', ''))
            if match_score_num >= 70:
                match_color = "#2ecc71"  # Green
                match_icon = "⭐"
            elif match_score_num >= 50:
                match_color = "#f39c12"  # Orange
                match_icon = "✅"
            else:
                match_color = "#e74c3c"  # Red
                match_icon = "⚠️"
            
            st.markdown(f"""
            <div class="candidate-card" style="border-left-color: {match_color};">
                <div class="candidate-name">{match_icon} {candidate['name']} - Match: {candidate['match_score']}</div>
                <div class="candidate-info">📧 Email: {candidate['email']}</div>
                <div class="candidate-info">📞 Phone: {candidate['phone']}</div>
                <div class="candidate-info">💼 Experience: {candidate['experience']}</div>
                <div class="candidate-info">🛠️ Skills: {candidate['skills'][:100]}{'...' if len(candidate['skills']) > 100 else ''}</div>
                <div class="candidate-info">📍 Location: {candidate['location']}</div>
                <div class="candidate-info">🎓 Education: {candidate['education']}</div>
                <div class="candidate-info">🆔 Unique ID: {candidate['unique_id'][:20]}...</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Individual download button
            file_path = resume_downloader.get_resume_file_path(candidate)
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Resume",
                        data=f.read(),
                        file_name=f"{candidate['name'].replace(' ', '_')}_resume.pdf",
                        mime="application/pdf",
                        key=f"download_{i}",
                        help=f"Download resume for {candidate['name']}"
                    )
            else:
                st.button(
                    "❌ Not Found",
                    disabled=True,
                    key=f"missing_{i}",
                    help="Resume file not found"
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Add statistics
    st.markdown("### 📊 Search Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Candidates", len(st.session_state.candidates))
    with col2:
        avg_match = sum([int(c['match_score'].replace('%', '')) for c in st.session_state.candidates]) / len(st.session_state.candidates)
        st.metric("Average Match", f"{avg_match:.1f}%")
    with col3:
        unique_skills = set()
        for c in st.session_state.candidates:
            if c['skills'] != 'Not specified':
                unique_skills.update([skill.strip() for skill in c['skills'].split(',')])
        st.metric("Unique Skills Found", len(unique_skills))

# Clear results button
if st.session_state.search_performed:
    if st.button("🗑️ Clear Results"):
        st.session_state.candidates = []
        st.session_state.search_performed = False
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm here to help you find the right candidates. Use the selection panel to specify your requirements."
        }]
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
