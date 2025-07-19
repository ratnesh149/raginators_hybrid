# 🌐 Web Integration Guide

This document explains how to use the integrated web interface for the Agentic HR Assistant.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. Start the Web Application
```bash
python start_web_app.py
```

### 4. Access the Interface
- **Main Interface**: http://localhost:5000
- **HR Assistant**: http://localhost:5000/hr_assistant.html
- **Original Forms**: Available through main interface

## 🎯 Features

### 🧠 HR Assistant Interface (`hr_assistant.html`)
The new HR Assistant interface provides:

#### Chat Interface
- **Natural Language Conversations**: Chat with the AI assistant
- **Quick Actions**: Pre-defined prompts for common tasks
- **Real-time Responses**: Instant AI-powered assistance

#### Candidate Shortlisting Tool
- **Smart Matching**: AI-powered candidate ranking
- **Flexible Filtering**: Experience level and skill requirements
- **Contact Information**: Direct access to candidate details
- **Match Scores**: Quantified compatibility ratings

#### Job Description Generator
- **Role-Specific Templates**: Industry-standard job descriptions
- **Department Integration**: Tailored for different departments
- **Experience Levels**: Junior to Lead level positions
- **Custom Requirements**: Add specific skills and qualifications

#### Hiring Checklist Generator
- **Process Automation**: Step-by-step hiring workflows
- **Interview Questions**: Role-specific question banks
- **Compliance Checks**: HR policy integration
- **Timeline Management**: Structured hiring process

## 🛠️ API Endpoints

The Flask backend provides these REST API endpoints:

### Chat API
```
POST /api/chat
Content-Type: application/json

{
  "message": "I want to hire a frontend developer"
}
```

### Candidate Shortlisting
```
POST /api/shortlist-candidates
Content-Type: application/json

{
  "requirements": "React, TypeScript, 5+ years",
  "min_experience": 5,
  "limit": 10
}
```

### Job Description Generation
```
POST /api/generate-job-description
Content-Type: application/json

{
  "role_title": "Senior Frontend Developer",
  "department": "Engineering",
  "experience_level": "Senior",
  "requirements": "React, TypeScript, Node.js"
}
```

### Hiring Checklist
```
POST /api/generate-checklist
Content-Type: application/json

{
  "role_title": "Data Scientist",
  "requirements": "Python, ML, Statistics"
}
```

### Similar Jobs Search
```
POST /api/search-similar-jobs
Content-Type: application/json

{
  "query": "python developer",
  "limit": 5
}
```

## 🏗️ Architecture

### Frontend (HTML/JavaScript)
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Dynamic content loading
- **Error Handling**: Graceful failure recovery
- **User Experience**: Intuitive interface design

### Backend (Flask)
- **RESTful APIs**: Clean endpoint design
- **CORS Support**: Cross-origin requests enabled
- **Error Handling**: Comprehensive error responses
- **Logging**: Detailed request/response logging

### Integration Layer
- **LangGraph Integration**: Direct access to agent workflows
- **Vector Database**: Seamless document search
- **State Management**: Session-aware conversations
- **Tool Orchestration**: Coordinated agent execution

## 📁 File Structure

```
raginators/
├── web_app.py                 # Flask web server
├── start_web_app.py          # Startup script
├── jobDescription/
│   ├── index.html            # Main interface (updated)
│   ├── hr_assistant.html     # New HR Assistant interface
│   ├── job_application_form.html
│   ├── view_applications.html
│   └── candidate_resumes.html
├── agents/                   # AI agents
├── services/                 # Vector database
├── tools/                    # Agent tools
└── graph/                    # LangGraph workflows
```

## 🔧 Customization

### Adding New Tools
1. Create tool function in `tools/` directory
2. Add API endpoint in `web_app.py`
3. Add UI component in `hr_assistant.html`
4. Update JavaScript handlers

### Styling Changes
- Modify CSS in `hr_assistant.html`
- Update color schemes and layouts
- Add new UI components as needed

### API Extensions
- Add new endpoints in `web_app.py`
- Implement corresponding agent logic
- Update frontend JavaScript calls

## 🐛 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Verify environment
cat .env

# Check port availability
lsof -i :5000
```

#### API Errors
- Check OpenAI API key in `.env`
- Verify vector database initialization
- Review server logs for detailed errors

#### No Candidates Found
```bash
# Initialize sample data
python manage_vectordb.py init-sample

# Verify database
python manage_vectordb.py search-candidates "python" --limit 5
```

#### Chat Not Working
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Test with curl commands

### Debug Mode
Enable detailed logging by setting `debug=True` in `web_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🚀 Production Deployment

### Environment Setup
```bash
# Use production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Security Considerations
- Set `debug=False` in production
- Use environment variables for secrets
- Implement rate limiting
- Add authentication if needed

### Performance Optimization
- Enable response caching
- Optimize vector database queries
- Use connection pooling
- Monitor resource usage

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error details
3. Test individual components (CLI, Streamlit, Web)
4. Verify all dependencies are installed correctly

## 🎉 Success!

Your Agentic HR Assistant is now fully integrated with a modern web interface! 

**Key Benefits:**
- ✅ **Unified Interface**: All HR tools in one place
- ✅ **Real-time AI**: Instant responses and recommendations
- ✅ **Professional UI**: Modern, responsive design
- ✅ **API-First**: Extensible architecture
- ✅ **Production Ready**: Scalable and maintainable

Visit http://localhost:5000/hr_assistant.html to start using your AI-powered HR assistant!
