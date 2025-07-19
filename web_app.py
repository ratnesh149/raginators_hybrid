from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from graph.stategraph import graph
from services.vector_db import HRVectorDB, get_vector_db
from tools.candidate_shortlist import candidate_shortlist_tool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='jobDescription',
            template_folder='jobDescription')
CORS(app)

# Initialize vector database service
vector_db = get_vector_db()

@app.route('/')
def index():
    """Serve the main HTML interface"""
    return send_from_directory('jobDescription', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from jobDescription folder"""
    return send_from_directory('jobDescription', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from the UI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        logger.info(f"Processing chat message: {user_message}")
        
        # Process through the graph
        responses = []
        for step in graph.stream({"messages": [("user", user_message)]}, subgraphs=True):
            state_data = step[1]
            
            for node_name, node_response in state_data.items():
                if node_name in ["chatbot", "jd_agent", "checklist_agent", "candidate_agent"]:
                    messages = node_response.get("messages", "")
                    
                    # Handle different message formats
                    if isinstance(messages, str):
                        content = messages
                    elif isinstance(messages, list):
                        content = " ".join([msg if isinstance(msg, str) else msg.content for msg in messages])
                    else:
                        content = str(messages)
                    
                    # Clean up content
                    if content.startswith("Chatbot needs clarification: "):
                        content = content[len("Chatbot needs clarification: "):]
                    
                    if content.strip():
                        responses.append({
                            'agent': node_name,
                            'content': content.strip()
                        })
        
        # Return the last meaningful response
        if responses:
            return jsonify({
                'success': True,
                'response': responses[-1]['content'],
                'agent': responses[-1]['agent']
            })
        else:
            return jsonify({
                'success': True,
                'response': "I'm here to help with your hiring needs. Could you please provide more details?",
                'agent': 'chatbot'
            })
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/shortlist-candidates', methods=['POST'])
def api_shortlist_candidates():
    """API endpoint for candidate shortlisting"""
    try:
        data = request.get_json()
        requirements = data.get('requirements', '')
        min_experience = data.get('min_experience', 0)
        limit = data.get('limit', 5)
        
        if not requirements:
            return jsonify({'error': 'Requirements are required'}), 400
        
        logger.info(f"Shortlisting candidates for: {requirements}")
        
        # Use the candidate shortlist tool
        result_text = candidate_shortlist_tool._run(
            job_requirements=requirements,
            min_experience=min_experience,
            n_candidates=limit
        )
        
        # Parse the result to extract structured data
        candidates = []
        if "No candidates found" not in result_text:
            # Extract candidate information from the formatted text
            lines = result_text.split('\n')
            current_candidate = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('**') and '. ' in line and '**' in line:
                    # New candidate
                    if current_candidate:
                        candidates.append(current_candidate)
                    
                    name = line.split('. ')[1].replace('**', '')
                    current_candidate = {
                        'name': name,
                        'score': 0.0,
                        'experience': 'Unknown',
                        'email': f"{name.lower().replace(' ', '.')}@email.com",
                        'phone': '(555) 123-4567',
                        'skills': 'Skills extracted from resume'
                    }
                elif 'Match Score:' in line:
                    try:
                        score_text = line.split('Match Score: ')[1].split('/')[0]
                        current_candidate['score'] = float(score_text)
                    except:
                        pass
                elif 'Experience:' in line:
                    try:
                        exp_text = line.split('Experience: ')[1].split(' years')[0]
                        current_candidate['experience'] = exp_text
                    except:
                        pass
            
            # Add the last candidate
            if current_candidate:
                candidates.append(current_candidate)
        
        return jsonify({
            'success': True,
            'candidates': candidates,
            'summary': {
                'total_found': len(candidates),
                'message': result_text
            },
            'total_found': len(candidates)
        })
        
    except Exception as e:
        logger.error(f"Error in shortlist endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/generate-job-description', methods=['POST'])
def api_generate_job_description():
    """API endpoint for job description generation"""
    try:
        data = request.get_json()
        role_title = data.get('role_title', '')
        requirements = data.get('requirements', '')
        experience_level = data.get('experience_level', '')
        department = data.get('department', '')
        
        if not role_title:
            return jsonify({'error': 'Role title is required'}), 400
        
        # Create a comprehensive prompt for the JD agent
        prompt = f"Create a job description for {role_title}"
        if department:
            prompt += f" in {department} department"
        if experience_level:
            prompt += f" at {experience_level} level"
        if requirements:
            prompt += f" with requirements: {requirements}"
        
        logger.info(f"Generating job description for: {prompt}")
        
        # Process through the graph
        for step in graph.stream({"messages": [("user", prompt)]}, subgraphs=True):
            state_data = step[1]
            
            for node_name, node_response in state_data.items():
                if node_name == "jd_agent":
                    messages = node_response.get("messages", "")
                    
                    if isinstance(messages, str):
                        content = messages
                    elif isinstance(messages, list):
                        content = " ".join([msg if isinstance(msg, str) else msg.content for msg in messages])
                    else:
                        content = str(messages)
                    
                    if content.strip():
                        return jsonify({
                            'success': True,
                            'job_description': content.strip()
                        })
        
        return jsonify({
            'success': False,
            'error': 'Could not generate job description'
        }), 500
        
    except Exception as e:
        logger.error(f"Error in job description endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/generate-checklist', methods=['POST'])
def api_generate_checklist():
    """API endpoint for hiring checklist generation"""
    try:
        data = request.get_json()
        role_title = data.get('role_title', '')
        requirements = data.get('requirements', '')
        
        if not role_title:
            return jsonify({'error': 'Role title is required'}), 400
        
        prompt = f"Create a hiring checklist for {role_title}"
        if requirements:
            prompt += f" with requirements: {requirements}"
        
        logger.info(f"Generating checklist for: {prompt}")
        
        # Process through the graph
        for step in graph.stream({"messages": [("user", prompt)]}, subgraphs=True):
            state_data = step[1]
            
            for node_name, node_response in state_data.items():
                if node_name == "checklist_agent":
                    messages = node_response.get("messages", "")
                    
                    if isinstance(messages, str):
                        content = messages
                    elif isinstance(messages, list):
                        content = " ".join([msg if isinstance(msg, str) else msg.content for msg in messages])
                    else:
                        content = str(messages)
                    
                    if content.strip():
                        return jsonify({
                            'success': True,
                            'checklist': content.strip()
                        })
        
        return jsonify({
            'success': False,
            'error': 'Could not generate checklist'
        }), 500
        
    except Exception as e:
        logger.error(f"Error in checklist endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/search-similar-jobs', methods=['POST'])
def api_search_similar_jobs():
    """API endpoint for searching similar job descriptions"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        logger.info(f"Searching similar jobs for: {query}")
        
        # Search in vector database
        results = vector_db.search_similar_jobs(query, limit=limit)
        
        return jsonify({
            'success': True,
            'similar_jobs': results
        })
        
    except Exception as e:
        logger.error(f"Error in similar jobs search: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Agentic HR Assistant API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Initialize sample data if needed
    try:
        vector_db.add_sample_data()
        logger.info("Vector database initialized with sample data")
    except Exception as e:
        logger.warning(f"Could not initialize sample data: {str(e)}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
