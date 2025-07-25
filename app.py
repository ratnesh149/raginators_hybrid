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

if "evaluation_performed" not in st.session_state:
    st.session_state.evaluation_performed = False

if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = {}

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
        
        # Job Description Generator button
        if st.button("📝 Generate Job Description", type="secondary"):
            if job_title:
                try:
                    from tools.job_description_generator import job_description_generator
                    
                    with st.spinner("Generating job description..."):
                        # Generate job description based on form inputs
                        job_desc = job_description_generator._run(
                            job_title=job_title,
                            required_skills=required_skills,
                            experience_level=experience_level,
                            location=location,
                            education=education,
                            company_name="Your Company",
                            department=""
                        )
                        
                        # Add to chat
                        st.session_state.messages.append({
                            "role": "user",
                            "content": f"Generate a job description for: {job_title}"
                        })
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Here's a professional job description based on your criteria:\n\n{job_desc}"
                        })
                        
                        st.success("✅ Job description generated successfully!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error generating job description: {str(e)}")
            else:
                st.warning("Please enter a job title first!")
        
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
                        
                        # NEW: Advanced Candidate Evaluation with 60% Accuracy Threshold
                        if st.session_state.candidates and filtered_results:
                            with st.spinner("🔍 Performing advanced candidate evaluation with 60% accuracy threshold..."):
                                try:
                                    from tools.candidate_evaluation import candidate_evaluation_tool
                                    
                                    # Create comprehensive job description for evaluation
                                    comprehensive_job_desc = f"""
Job Title: {job_title}

Required Skills: {', '.join(required_skills) if required_skills else 'Not specified'}

Experience Level: {experience_level}
Minimum Experience: {min_exp} years
Maximum Experience: {max_exp} years

Location: {location if location else 'Not specified'}
Education: {education if education else 'Not specified'}

Job Requirements:
{generated_query}
                                    """.strip()
                                    
                                    # Get evaluation results using the new evaluation tool
                                    evaluation_summary = candidate_evaluation_tool.get_evaluation_summary(
                                        candidates=filtered_results,  # Use original candidate objects
                                        job_description=comprehensive_job_desc
                                    )
                                    
                                    if 'error' not in evaluation_summary:
                                        # Store evaluation results in session state
                                        st.session_state.evaluation_results = evaluation_summary
                                        st.session_state.evaluation_performed = True
                                        
                                        # Update candidates list with evaluation scores and status
                                        selected_candidates = evaluation_summary.get('selected_candidates', [])
                                        rejected_candidates = evaluation_summary.get('rejected_candidates', [])
                                        
                                        # Re-create candidates list with evaluation data
                                        evaluated_candidates_list = []
                                        
                                        # Add selected candidates first (60%+ accuracy)
                                        for eval_result in selected_candidates:
                                            candidate = eval_result['candidate']
                                            score = eval_result['score']
                                            justification = eval_result['justification']
                                            metadata = candidate.get('metadata', {})
                                            
                                            candidate_info = {
                                                "name": metadata.get('candidate_name', 'Unknown'),
                                                "experience": f"{metadata.get('experience_years', 'Unknown')} years",
                                                "skills": metadata.get('skills', 'Not specified'),
                                                "email": metadata.get('email', 'Not available'),
                                                "phone": metadata.get('phone', 'Not available'),
                                                "education": metadata.get('education', 'Not specified'),
                                                "location": metadata.get('location', 'Not specified'),
                                                "match_score": f"{score.overall_score:.1%}",
                                                "evaluation_status": "SELECTED ⭐",
                                                "evaluation_score": score.overall_score,
                                                "selection_reasons": justification.get('selection_reasons', []),
                                                "unique_id": metadata.get('unique_id', f'selected_{len(evaluated_candidates_list)}'),
                                                "pdf_file_path": metadata.get('pdf_file_path', ''),
                                                "pdf_filename": metadata.get('pdf_filename', ''),
                                                "skills_score": f"{score.skills_alignment:.1%}",
                                                "experience_score": f"{score.experience_mapping:.1%}",
                                                "semantic_score": f"{score.semantic_similarity:.1%}",
                                                "cert_score": f"{score.certification_score:.1%}",
                                                "role_fit_score": f"{score.role_fit_score:.1%}",
                                                "recommendation": justification.get('recommendation', '')
                                            }
                                            evaluated_candidates_list.append(candidate_info)
                                        
                                        # Add rejected candidates (below 60% accuracy)
                                        for eval_result in rejected_candidates:
                                            candidate = eval_result['candidate']
                                            score = eval_result['score']
                                            justification = eval_result['justification']
                                            metadata = candidate.get('metadata', {})
                                            
                                            candidate_info = {
                                                "name": metadata.get('candidate_name', 'Unknown'),
                                                "experience": f"{metadata.get('experience_years', 'Unknown')} years",
                                                "skills": metadata.get('skills', 'Not specified'),
                                                "email": metadata.get('email', 'Not available'),
                                                "phone": metadata.get('phone', 'Not available'),
                                                "education": metadata.get('education', 'Not specified'),
                                                "location": metadata.get('location', 'Not specified'),
                                                "match_score": f"{score.overall_score:.1%}",
                                                "evaluation_status": "REJECTED",
                                                "evaluation_score": score.overall_score,
                                                "rejection_reasons": justification.get('rejection_reasons', []),
                                                "unique_id": metadata.get('unique_id', f'rejected_{len(evaluated_candidates_list)}'),
                                                "pdf_file_path": metadata.get('pdf_file_path', ''),
                                                "pdf_filename": metadata.get('pdf_filename', ''),
                                                "skills_score": f"{score.skills_alignment:.1%}",
                                                "experience_score": f"{score.experience_mapping:.1%}",
                                                "semantic_score": f"{score.semantic_similarity:.1%}",
                                                "cert_score": f"{score.certification_score:.1%}",
                                                "role_fit_score": f"{score.role_fit_score:.1%}",
                                                "recommendation": justification.get('recommendation', '')
                                            }
                                            evaluated_candidates_list.append(candidate_info)
                                        
                                        # Update session state with evaluated candidates
                                        st.session_state.candidates = evaluated_candidates_list
                                        
                                        # Show evaluation summary
                                        summary = evaluation_summary.get('summary', {})
                                        selected_count = summary.get('selected_count', 0)
                                        rejected_count = summary.get('rejected_count', 0)
                                        avg_score = summary.get('average_score', '0%')
                                        selection_rate = summary.get('selection_rate', '0%')
                                        
                                        st.success(f"🎯 **Advanced Evaluation Complete!**\n\n"
                                                 f"✅ **Selected**: {selected_count} candidates (≥60% accuracy)\n"
                                                 f"❌ **Rejected**: {rejected_count} candidates (<60% threshold)\n"
                                                 f"📊 **Average Score**: {avg_score}\n"
                                                 f"📈 **Selection Rate**: {selection_rate}")
                                        
                                        # Show detailed evaluation criteria used
                                        criteria = summary.get('evaluation_criteria', {})
                                        st.info(f"🔍 **Evaluation Criteria Applied:**\n"
                                               f"• Required Skills: {criteria.get('required_skills_count', 0)} skills\n"
                                               f"• Experience Range: {criteria.get('experience_range', 'Any')}\n"
                                               f"• Role Level: {criteria.get('role_level', 'Any').title()}\n"
                                               f"• Certifications: {'Required' if criteria.get('certifications_required') else 'Optional'}")
                                    
                                    else:
                                        st.error(f"Evaluation failed: {evaluation_summary['error']}")
                                        logger.error(f"Evaluation error: {evaluation_summary['error']}")
                                    
                                except Exception as e:
                                    st.error(f"Error during advanced evaluation: {str(e)}")
                                    logger.error(f"Evaluation error: {e}")
                                    # Continue with original candidates if evaluation fails
                                    pass
                        
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
                        
                        # Record search interaction for training
                        try:
                            from services.training_system import training_system
                            
                            search_data = {
                                "job_title": job_title,
                                "required_skills": required_skills,
                                "experience_level": experience_level,
                                "location": location,
                                "education": education,
                                "num_candidates": num_candidates
                            }
                            
                            training_system.record_search_interaction(
                                search_data=search_data,
                                results=st.session_state.candidates,
                                user_feedback=None  # Could be enhanced with user feedback later
                            )
                        except Exception as training_error:
                            logger.warning(f"Training system error: {training_error}")
                        
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
    
    # Add view options
    st.markdown("### 👀 View Options")
    view_mode = st.radio(
        "Choose how to display candidates:",
        ["📋 Detailed Cards View", "📊 Table Summary View"],
        horizontal=True
    )
    
    if view_mode == "📊 Table Summary View":
        # Create a comprehensive table view
        st.markdown("### 📊 All Candidates Summary Table")
        
        # Prepare data for table
        table_data = []
        for candidate in st.session_state.candidates:
            evaluation_status = candidate.get('evaluation_status', 'NOT_EVALUATED')
            
            # Determine status emoji and text
            if evaluation_status.startswith('SELECTED'):
                status_display = "✅ SELECTED"
                priority = 1
            elif evaluation_status == 'REJECTED':
                status_display = "❌ REJECTED"
                priority = 2
            else:
                status_display = "📋 NOT EVALUATED"
                priority = 3
            
            # Get evaluation score or match score
            try:
                if candidate.get('evaluation_score'):
                    eval_score = candidate['evaluation_score']
                    if isinstance(eval_score, (int, float)):
                        score_display = f"{eval_score:.1%}"
                    else:
                        score_display = str(eval_score)
                else:
                    score_display = candidate.get('match_score', 'N/A')
            except:
                score_display = candidate.get('match_score', 'N/A')
            
            # Get primary reason
            primary_reason = "N/A"
            if candidate.get('selection_reasons'):
                primary_reason = candidate['selection_reasons'][0][:100] + "..." if len(candidate['selection_reasons'][0]) > 100 else candidate['selection_reasons'][0]
            elif candidate.get('rejection_reasons'):
                primary_reason = candidate['rejection_reasons'][0][:100] + "..." if len(candidate['rejection_reasons'][0]) > 100 else candidate['rejection_reasons'][0]
            
            # Check if resume is available
            file_path = resume_downloader.get_resume_file_path(candidate)
            resume_available = "✅ Available" if file_path and os.path.exists(file_path) else "❌ Not Found"
            
            table_data.append({
                'Priority': priority,
                'Name': candidate['name'],
                'Status': status_display,
                'Score': score_display,
                'Experience': candidate['experience'],
                'Email': candidate['email'],
                'Phone': candidate['phone'],
                'Key Skills': candidate['skills'][:50] + "..." if len(candidate['skills']) > 50 else candidate['skills'],
                'Primary Reason': primary_reason,
                'Resume': resume_available,
                'Unique ID': candidate.get('unique_id', 'N/A')[:15] + "..."
            })
        
        # Sort by priority (selected first, then rejected, then not evaluated)
        table_data.sort(key=lambda x: x['Priority'])
        
        # Remove priority column for display
        display_data = [{k: v for k, v in row.items() if k != 'Priority'} for row in table_data]
        
        # Display the table
        if display_data:
            # Use simple dataframe display for better compatibility
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Add bulk download options below table
            st.markdown("### 📦 Bulk Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download all resumes
                if st.button("📦 Download All Resumes (ZIP)", type="primary"):
                    with st.spinner("Creating ZIP file with all resumes..."):
                        zip_path = resume_downloader.create_bulk_download_zip(st.session_state.candidates)
                        if zip_path:
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download ZIP File",
                                    data=f.read(),
                                    file_name=f"all_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                    mime="application/zip",
                                    key="bulk_download_all"
                                )
            
            with col2:
                # Download selected candidates only
                selected_only = [c for c in st.session_state.candidates if c.get('evaluation_status', '').startswith('SELECTED')]
                if selected_only:
                    if st.button("✅ Download Selected Only (ZIP)", type="secondary"):
                        with st.spinner("Creating ZIP file with selected candidates..."):
                            zip_path = resume_downloader.create_bulk_download_zip(selected_only)
                            if zip_path:
                                with open(zip_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download Selected ZIP",
                                        data=f.read(),
                                        file_name=f"selected_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                        mime="application/zip",
                                        key="bulk_download_selected"
                                    )
            
            with col3:
                # Export candidate data as CSV
                csv_content = resume_downloader.create_candidates_csv(st.session_state.candidates)
                if csv_content:
                    st.download_button(
                        label="📊 Export as CSV",
                        data=csv_content,
                        file_name=f"candidates_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="export_csv"
                    )
        else:
            st.info("No candidate data available for table view.")
    
    else:
        # Detailed Cards View
        
        # First, separate candidates by evaluation status
        selected_candidates = [c for c in st.session_state.candidates if c.get('evaluation_status', '').startswith('SELECTED')]
        rejected_candidates = [c for c in st.session_state.candidates if c.get('evaluation_status') == 'REJECTED']
        not_evaluated_candidates = [c for c in st.session_state.candidates if c.get('evaluation_status', 'NOT_EVALUATED') == 'NOT_EVALUATED']
        
        # Display Selected Candidates First (if any)
        if selected_candidates:
            st.subheader("✅ Selected Candidates (60%+ Match)")
            st.success(f"Found {len(selected_candidates)} candidates that meet the 60% accuracy threshold")
            
            for i, candidate in enumerate(selected_candidates):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        # Candidate basic info
                        st.markdown(f"""
                        **🌟 {candidate['name']}**  
                        📧 **Email:** {candidate['email']}  
                        📞 **Phone:** {candidate['phone']}  
                        💼 **Experience:** {candidate['experience']}  
                        🎓 **Education:** {candidate['education']}  
                        🛠️ **Skills:** {candidate['skills'][:150]}{'...' if len(candidate['skills']) > 150 else ''}
                        """)
                    
                    with col2:
                        # Evaluation scores and reasons
                        st.markdown("**📊 Evaluation Results:**")
                        try:
                            eval_score = candidate.get('evaluation_score', 0)
                            if isinstance(eval_score, (int, float)):
                                st.markdown(f"**Overall Score:** {eval_score:.1%}")
                            else:
                                st.markdown(f"**Overall Score:** {eval_score}")
                        except:
                            st.markdown(f"**Overall Score:** {candidate.get('evaluation_score', 'N/A')}")
                        
                        # Display detailed scores
                        if candidate.get('skills_score'):
                            try:
                                st.markdown(f"• Skills Match: {candidate['skills_score']}")
                                st.markdown(f"• Experience Fit: {candidate['experience_score']}")
                                st.markdown(f"• Semantic Match: {candidate['semantic_score']}")
                                st.markdown(f"• Role Fit: {candidate.get('role_fit_score', 'N/A')}")
                            except Exception as e:
                                st.markdown("• Detailed scores: Available in evaluation data")
                        
                        # Selection reasons
                        if candidate.get('selection_reasons'):
                            st.markdown("**🎯 Selection Reasons:**")
                            for reason in candidate['selection_reasons'][:3]:  # Show top 3 reasons
                                st.markdown(f"• {reason}")
                            
                            if len(candidate['selection_reasons']) > 3:
                                with st.expander("View All Reasons"):
                                    for reason in candidate['selection_reasons'][3:]:
                                        st.markdown(f"• {reason}")
                    
                    with col3:
                        # Download button
                        file_path = resume_downloader.get_resume_file_path(candidate)
                        if file_path and os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="📄 Download Resume",
                                    data=f.read(),
                                    file_name=f"{candidate['name'].replace(' ', '_')}_resume.pdf",
                                    mime="application/pdf",
                                    key=f"download_selected_{i}",
                                    help=f"Download resume for {candidate['name']}",
                                    type="primary"
                                )
                        else:
                            st.button(
                                "❌ Resume Not Found",
                                disabled=True,
                                key=f"missing_selected_{i}",
                                help="Resume file not available"
                            )
                    
                    st.markdown("---")
        
        # Display Rejected Candidates
        if rejected_candidates:
            st.subheader("❌ Rejected Candidates (Below 60% Threshold)")
            st.info(f"Found {len(rejected_candidates)} candidates that didn't meet the 60% threshold but may still be worth reviewing")
            
            # Option to show/hide rejected candidates
            show_rejected = st.checkbox("Show Rejected Candidates Details", value=True)
            
            if show_rejected:
                for i, candidate in enumerate(rejected_candidates):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            # Candidate basic info
                            st.markdown(f"""
                            **{candidate['name']}**  
                            📧 **Email:** {candidate['email']}  
                            📞 **Phone:** {candidate['phone']}  
                            💼 **Experience:** {candidate['experience']}  
                            🎓 **Education:** {candidate['education']}  
                            🛠️ **Skills:** {candidate['skills'][:150]}{'...' if len(candidate['skills']) > 150 else ''}
                            """)
                        
                        with col2:
                            # Evaluation scores and rejection reasons
                            st.markdown("**📊 Evaluation Results:**")
                            try:
                                eval_score = candidate.get('evaluation_score', 0)
                                if isinstance(eval_score, (int, float)):
                                    st.markdown(f"**Overall Score:** {eval_score:.1%}")
                                else:
                                    st.markdown(f"**Overall Score:** {eval_score}")
                            except:
                                st.markdown(f"**Overall Score:** {candidate.get('evaluation_score', 'N/A')}")
                            
                            # Display detailed scores
                            if candidate.get('skills_score'):
                                try:
                                    st.markdown(f"• Skills Match: {candidate['skills_score']}")
                                    st.markdown(f"• Experience Fit: {candidate['experience_score']}")
                                    st.markdown(f"• Semantic Match: {candidate['semantic_score']}")
                                    st.markdown(f"• Role Fit: {candidate.get('role_fit_score', 'N/A')}")
                                except Exception as e:
                                    st.markdown("• Detailed scores: Available in evaluation data")
                            
                            # Rejection reasons
                            if candidate.get('rejection_reasons'):
                                st.markdown("**❌ Rejection Reasons:**")
                                for reason in candidate['rejection_reasons'][:3]:  # Show top 3 reasons
                                    st.markdown(f"• {reason}")
                                
                                if len(candidate['rejection_reasons']) > 3:
                                    with st.expander("View All Reasons"):
                                        for reason in candidate['rejection_reasons'][3:]:
                                            st.markdown(f"• {reason}")
                            
                            # Show recommendation
                            if candidate.get('recommendation'):
                                st.markdown(f"**💡 Assessment:** {candidate['recommendation']}")
                        
                        with col3:
                            # Download button
                            file_path = resume_downloader.get_resume_file_path(candidate)
                            if file_path and os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="📄 Download Resume",
                                        data=f.read(),
                                        file_name=f"{candidate['name'].replace(' ', '_')}_resume.pdf",
                                        mime="application/pdf",
                                        key=f"download_rejected_{i}",
                                        help=f"Download resume for {candidate['name']}",
                                        type="secondary"
                                    )
                            else:
                                st.button(
                                    "❌ Resume Not Found",
                                    disabled=True,
                                    key=f"missing_rejected_{i}",
                                    help="Resume file not available"
                                )
                        
                        st.markdown("---")
        
        # Display Not Evaluated Candidates (fallback for old data)
        if not_evaluated_candidates:
            st.subheader("📋 Additional Candidates (Not Evaluated)")
            st.warning(f"Found {len(not_evaluated_candidates)} candidates from previous searches that haven't been evaluated yet")
            
            # Option to show/hide not evaluated candidates
            show_not_evaluated = st.checkbox("Show Not Evaluated Candidates", value=False)
            
            if show_not_evaluated:
                for i, candidate in enumerate(not_evaluated_candidates):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            # Candidate basic info
                            st.markdown(f"""
                            **{candidate['name']}**  
                            📧 **Email:** {candidate['email']}  
                            📞 **Phone:** {candidate['phone']}  
                            💼 **Experience:** {candidate['experience']}  
                            🎓 **Education:** {candidate['education']}  
                            🛠️ **Skills:** {candidate['skills'][:150]}{'...' if len(candidate['skills']) > 150 else ''}
                            """)
                        
                        with col2:
                            # Basic match score (old system)
                            st.markdown("**📊 Basic Match Score:**")
                            st.markdown(f"**Match Score:** {candidate.get('match_score', 'N/A')}")
                            st.markdown("*Advanced evaluation not performed*")
                            
                            # Show unique ID for reference
                            st.markdown(f"**🆔 ID:** {candidate.get('unique_id', 'N/A')[:20]}...")
                        
                        with col3:
                            # Download button
                            file_path = resume_downloader.get_resume_file_path(candidate)
                            if file_path and os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="📄 Download Resume",
                                        data=f.read(),
                                        file_name=f"{candidate['name'].replace(' ', '_')}_resume.pdf",
                                        mime="application/pdf",
                                        key=f"download_not_eval_{i}",
                                        help=f"Download resume for {candidate['name']}"
                                    )
                            else:
                                st.button(
                                    "❌ Resume Not Found",
                                    disabled=True,
                                    key=f"missing_not_eval_{i}",
                                    help="Resume file not available"
                                )
                        
                        st.markdown("---")
        
        # Summary section at the bottom
        st.markdown("### 📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", len(st.session_state.candidates))
        with col2:
            st.metric("✅ Selected", len(selected_candidates), delta=f"{len(selected_candidates)/len(st.session_state.candidates)*100:.1f}%" if st.session_state.candidates else "0%")
        with col3:
            st.metric("❌ Rejected", len(rejected_candidates), delta=f"{len(rejected_candidates)/len(st.session_state.candidates)*100:.1f}%" if st.session_state.candidates else "0%")
        with col4:
            st.metric("📋 Not Evaluated", len(not_evaluated_candidates))
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Add statistics with evaluation metrics
    st.markdown("### 📊 Search & Evaluation Statistics")
    
    # Check if evaluation was performed
    if st.session_state.get('evaluation_performed', False):
        # Enhanced statistics with evaluation data
        col1, col2, col3, col4 = st.columns(4)
        
        selected_count = len([c for c in st.session_state.candidates if c.get('evaluation_status', '').startswith('SELECTED')])
        rejected_count = len([c for c in st.session_state.candidates if c.get('evaluation_status') == 'REJECTED'])
        
        with col1:
            st.metric("Total Evaluated", len(st.session_state.candidates))
        with col2:
            st.metric("✅ Selected (60%+)", selected_count, delta=f"{selected_count/len(st.session_state.candidates)*100:.1f}%")
        with col3:
            st.metric("❌ Rejected (<60%)", rejected_count, delta=f"{rejected_count/len(st.session_state.candidates)*100:.1f}%")
        with col4:
            # Calculate average evaluation score
            eval_scores = [c.get('evaluation_score', 0) for c in st.session_state.candidates if c.get('evaluation_score')]
            avg_eval_score = sum(eval_scores) / len(eval_scores) if eval_scores else 0
            st.metric("Average Score", f"{avg_eval_score:.1%}")
        
        # Additional evaluation insights
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Skills analysis
            skills_scores = [c.get('skills_score', 0) for c in st.session_state.candidates if c.get('skills_score')]
            avg_skills = sum(skills_scores) / len(skills_scores) if skills_scores else 0
            st.metric("Avg Skills Match", f"{avg_skills:.1%}")
        
        with col2:
            # Experience analysis
            exp_scores = [c.get('experience_score', 0) for c in st.session_state.candidates if c.get('experience_score')]
            avg_exp = sum(exp_scores) / len(exp_scores) if exp_scores else 0
            st.metric("Avg Experience Fit", f"{avg_exp:.1%}")
        
        with col3:
            # Semantic analysis
            semantic_scores = [c.get('semantic_score', 0) for c in st.session_state.candidates if c.get('semantic_score')]
            avg_semantic = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0
            st.metric("Avg Semantic Match", f"{avg_semantic:.1%}")
    
    else:
        # Original statistics if no evaluation performed
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Candidates", len(st.session_state.candidates))
        with col2:
            # Fix TypeError by safely handling match_score values
            try:
                match_scores = []
                for c in st.session_state.candidates:
                    match_score = c.get('match_score', '0%')
                    if isinstance(match_score, str) and '%' in match_score:
                        match_scores.append(int(match_score.replace('%', '')))
                    elif isinstance(match_score, (int, float)):
                        match_scores.append(int(match_score * 100) if match_score <= 1 else int(match_score))
                    else:
                        match_scores.append(0)
                
                avg_match = sum(match_scores) / len(match_scores) if match_scores else 0
                st.metric("Average Match", f"{avg_match:.1f}%")
            except Exception as e:
                st.metric("Average Match", "N/A")
        with col3:
            unique_skills = set()
            for c in st.session_state.candidates:
                if c['skills'] != 'Not specified':
                    unique_skills.update([skill.strip() for skill in c['skills'].split(',')])
            st.metric("Unique Skills Found", len(unique_skills))

# Training Insights Section
if st.session_state.search_performed:
    with st.expander("🧠 AI Learning Insights", expanded=False):
        try:
            from services.training_system import training_system
            
            # Get training summary
            summary = training_system.get_training_summary()
            
            st.markdown("### 📈 System Learning Progress")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Searches", summary["total_searches"])
            with col2:
                st.metric("Success Rate", f"{summary['overall_success_rate']:.1f}%")
            with col3:
                st.metric("Training Data Points", summary["training_data_size"])
            
            # Field effectiveness
            if summary["field_effectiveness"]:
                st.markdown("### 🎯 Field Effectiveness")
                for field, data in summary["field_effectiveness"].items():
                    field_name = field.replace("_", " ").title()
                    effectiveness = data["effectiveness_percentage"]
                    
                    # Color code based on effectiveness
                    if effectiveness >= 70:
                        color = "green"
                        icon = "🟢"
                    elif effectiveness >= 50:
                        color = "orange"
                        icon = "🟡"
                    else:
                        color = "red"
                        icon = "🔴"
                    
                    st.markdown(f"{icon} **{field_name}**: {effectiveness:.1f}% effective ({data['successful_uses']}/{data['total_uses']} searches)")
            
            # Skill recommendations for current job title
            if 'job_title' in locals() and job_title:
                recommendations = training_system.get_skill_recommendations(job_title)
                if recommendations:
                    st.markdown("### 💡 Recommended Skills for This Role")
                    st.info(f"Based on training data, these skills are commonly successful for **{job_title}**: {', '.join(recommendations[:5])}")
            
            # Experience level insights
            if 'experience_level' in locals() and experience_level != "Any":
                insights = training_system.get_experience_insights(experience_level)
                if insights["total_searches"] > 0:
                    st.markdown(f"### 📊 {experience_level} Insights")
                    st.markdown(f"**Success Rate**: {insights['success_rate']:.1f}% | **Avg Results**: {insights['average_results']} | **Searches**: {insights['total_searches']}")
                    st.markdown(f"**Recommendation**: {insights['recommendation']}")
            
            # Popular successful combinations
            popular_combos = training_system.get_popular_combinations()
            if popular_combos:
                st.markdown("### 🏆 Most Successful Search Combinations")
                for i, combo in enumerate(popular_combos[:3], 1):
                    st.markdown(f"**{i}.** {combo['job_title']} | {combo['experience_level']} | Skills: {combo['key_skills'][:30]}...")
                    st.markdown(f"   *Success: {combo['success_score']} good matches from {combo['results_count']} results*")
            
        except Exception as e:
            st.warning("Training insights temporarily unavailable")

# Clear results button
if st.session_state.search_performed:
    if st.button("🗑️ Clear Results"):
        st.session_state.candidates = []
        st.session_state.search_performed = False
        st.session_state.evaluation_performed = False
        st.session_state.evaluation_results = {}
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I'm here to help you find the right candidates. Use the selection panel to specify your requirements."
        }]
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
