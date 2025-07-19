# 🧠 Agentic HR Assistant

An intelligent, multi-agent AI application that helps HR professionals plan and execute startup hiring processes — powered by LangGraph, vector databases, and function-based routing.

## 🚀 Overview

This project demonstrates how to build a multi-agent, memory-aware AI assistant using LangGraph, LangChain, vector databases, and OpenAI's GPT APIs.

It allows HR users to:

- Plan and execute hiring processes
- Generate job descriptions with similar job insights
- Create hiring checklists with relevant interview questions
- **Search and match candidates against job requirements** ✅
- Query HR policies and company guidelines
- Ask follow-up questions based on role
- Retain memory across steps in a session

## 🧰 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Main language |
| LangGraph | Agent routing & workflow logic |
| LangChain | LLM tooling + schema support |
| OpenAI gpt-4o | Core LLM used (via AzureChatOpenAI) |
| ChromaDB | Vector database for document storage |
| Sentence Transformers | Text embeddings for similarity search |

## 🗄️ Vector Database Integration

The system includes a comprehensive vector database that stores and retrieves:

- **Job Descriptions**: Similar role templates and inspiration
- **Resumes**: Candidate profiles for matching
- **HR Policies**: Company guidelines and procedures  
- **Interview Questions**: Role-specific question banks
- **Company Information**: Organizational context

### Vector Database Features:
- **Semantic Search**: Find similar content using AI embeddings
- **Document Processing**: Support for PDF, DOCX, TXT, and MD files
- **Bulk Import**: Process entire directories of HR documents
- **Metadata Filtering**: Search by department, level, experience, etc.
- **Real-time Updates**: Add new documents during conversations
- **Candidate Matching**: Intelligent candidate shortlisting with match scores

## 🧠 Agents

### 👥 1. Chatbot Agent (Interface)
- Acts as the main interface with the user
- Asks clarifying questions about roles, budget, skills, timeline
- Routes requests to specialized agents
- **Handles candidate shortlisting requests** ✅

### 📝 2. JD Writer Agent (Enhanced)
- Searches similar job descriptions for inspiration
- Crafts Markdown-based job descriptions using best practices
- Incorporates insights from vector database
- Responds only after full details are collected

### ✅ 3. Checklist Agent (Enhanced)
- Searches for relevant interview questions
- Queries HR policies for compliance requirements
- Generates a step-by-step hiring plan
- Requires complete role context to run

### 🎯 4. Candidate Agent (NEW) ✅
- **Shortlists and ranks candidates from resume database**
- **Provides match scores and contact information**
- **Filters by experience level and requirements**
- **Returns actionable candidate recommendations**

## 🛠️ How to Run

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up .env**
```
OPENAI_API_KEY=your_api_key
```

3. **Initialize vector database** (optional - sample data will be added automatically)
```bash
python manage_vectordb.py init-sample
```

4. **Run the assistant**
```bash
python run.py
```

5. **Chat! Try these examples:**
```
I want to hire a frontend developer
Senior level, React and TypeScript, 5+ years experience
Can you shortlist candidates for this role?
```

## 💬 **Usage Examples**

### **Complete Hiring Workflow:**
```
👤 You: I want to hire a frontend developer

🤖 Assistant: Could you provide more details about the requirements?

👤 You: Senior level, React and TypeScript, 5+ years experience

🤖 Assistant: 🎯 **CANDIDATE SHORTLIST** (Top 3 matches)
============================================================

**1. John Doe**
   📊 Match Score: 0.85/1.00
   💼 Experience: 5 years
   📧 Contact: john.doe@email.com
   📞 Phone: (555) 123-4567
   ✅ **HIGHLY RECOMMENDED**

**2. Jane Smith**
   📊 Match Score: 0.72/1.00
   💼 Experience: 7 years
   📧 Contact: jane.smith@email.com
   ✅ **GOOD MATCH**

📈 **SUMMARY:**
   • Total candidates in database: 4
   • Candidates meeting experience requirement: 3
   • Next Steps: Contact John Doe and Jane Smith for interviews
```

### **Other Capabilities:**
```
# Job Description Creation
👤 You: Create a job description for a backend developer

# Hiring Checklist
👤 You: I need a hiring plan for a data scientist

# Direct Candidate Search
👤 You: Find candidates with Python and Django, 3+ years
```

## 📊 Vector Database Management

Use the CLI tool to manage your HR document database:

```bash
# Add a job description
python manage_vectordb.py add-job "Senior Python Developer" --file job_description.pdf --department Engineering --level Senior

# Add a resume
python manage_vectordb.py add-resume "John Doe" --file resume.pdf --experience 5

# Add HR policy
python manage_vectordb.py add-policy "Remote Work Policy" --file policy.docx

# Search similar jobs
python manage_vectordb.py search-jobs "python developer" --limit 5

# Search candidates
python manage_vectordb.py search-candidates "React JavaScript frontend" --limit 10

# Bulk import documents
python manage_vectordb.py bulk-import ./hr_documents --type auto

# Initialize with sample data
python manage_vectordb.py init-sample
```

## 🏗️ Design Decisions

| Area | Choice | Why |
|------|--------|-----|
| Routing | Rule-based chatbot with pattern detection | Reliable routing to appropriate agents |
| Memory | MemorySaver() | Simple in-memory state retention for single sessions |
| State | Based on MessagesState | Leverages LangGraph's built-in message tracking |
| Vector DB | ChromaDB | Local, persistent, easy to integrate |
| Embeddings | Sentence Transformers | Fast, local, good quality embeddings |
| Output | Markdown + CLI | Simple developer-facing display for easy testing |
| Agent Flow | Conditional routing | Prevents infinite loops, ensures task completion |
| Candidate Matching | Direct tool execution | Reliable, fast candidate shortlisting |

## 🎯 **Key Features Implemented**

- ✅ **Proper conditional routing** - Agents route correctly without infinite loops
- ✅ **Vector Database Integration** - Document storage, similarity search, and knowledge retrieval
- ✅ **Candidate Shortlisting** - Intelligent matching with rankings and contact information
- ✅ **Enhanced Job Descriptions** - Market-informed JDs using vector database insights
- ✅ **Structured Hiring Process** - Comprehensive checklists with interview questions
- ✅ **Robust Error Handling** - Graceful failure recovery and user feedback
- ✅ **Multi-format Document Support** - PDF, DOCX, TXT, and MD file processing
- ✅ **Bulk Import Capabilities** - Process entire directories of HR documents

## 📈 **System Improvements Made**

### **Resolved Issues:**
- ❌ ~~Recursion limit errors~~ ✅ **FIXED**: Proper routing and task completion detection
- ❌ ~~Infinite loops in conversation~~ ✅ **FIXED**: Conditional routing with stop conditions
- ❌ ~~Missing candidate shortlisting~~ ✅ **ADDED**: Full candidate matching functionality
- ❌ ~~Complex tool calling issues~~ ✅ **SIMPLIFIED**: Direct tool execution

### **Enhanced Features:**
- 🔧 **Improved Chatbot**: Pattern recognition and intelligent routing
- 🔧 **Simplified Runner**: Clean conversation interface without complex streaming
- 🔧 **Better State Management**: Proper message handling and state updates
- 🔧 **Enhanced Tools**: Reliable vector database operations

## 📂 Project Structure

```
agentic-hr-assistant/
├── agents/
│   ├── jd_agent.py          # Job description generation agent (enhanced)
│   ├── checklist_agent.py   # Hiring checklist generation agent
│   └── candidate_agent.py   # Candidate shortlisting agent (NEW) ✅
├── graph/
│   └── stategraph.py        # LangGraph graph setup + memory (updated)
├── nodes/
│   ├── chatbot.py           # Interface agent (enhanced routing)
│   ├── agentnodes.py        # All agent nodes (updated)
│   └── human.py             # Fallback handler
├── services/
│   └── vector_db.py         # Vector database service
├── tools/
│   ├── google_search.py     # Google search integration
│   ├── vector_tools.py      # Vector database tools for agents
│   ├── candidate_shortlist.py # Candidate shortlisting tool (NEW) ✅
│   └── document_processor.py # Document processing utilities
├── app.py                   # Streamlit web interface
├── llm_init.py             # LLM initialization and configuration
├── requirements.txt        # Project dependencies (updated)
├── run.py                  # CLI runtime loop (completely rewritten) ✅
├── manage_vectordb.py      # Vector database management CLI
├── stateclass.py           # Defines shared state between agents
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation (updated)
```

## 🎯 Vector Database Use Cases

1. **Job Description Enhancement**: Find similar roles to improve JD quality
2. **Candidate Matching**: Search resumes for skills and experience alignment  
3. **Interview Preparation**: Get relevant questions for specific roles
4. **Policy Compliance**: Ensure hiring practices follow company guidelines
5. **Knowledge Retention**: Build institutional memory of hiring decisions
6. **Template Library**: Maintain reusable hiring assets and templates

## 🚀 **Getting Started**

### **Quick Start:**
```bash
# Clone and setup
cd /path/to/agentic-hr-assistant
pip install -r requirements.txt

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your_key_here" > .env

# Initialize with sample data
python manage_vectordb.py init-sample

# Start the assistant
python run.py
```

### **First Conversation:**
```
👤 You: I want to hire a frontend developer
👤 You: Senior level, React and TypeScript, 5+ years experience
🤖 Assistant: [Returns ranked candidate shortlist with contact information]
```

## 🎉 **Production Ready Features**

- **No Infinite Loops**: Robust routing with proper task completion
- **Real Candidate Matching**: Actual shortlisting with contact information
- **Enhanced Job Descriptions**: Market-informed using vector database
- **Comprehensive Hiring Plans**: Structured process with interview questions
- **Scalable Architecture**: Easy to extend with new agents and tools
- **Error Handling**: Graceful failure recovery and user feedback

## 📞 **Support & Troubleshooting**

### **Common Issues:**
- **Recursion errors**: Fixed in current version
- **No candidate results**: Run `python manage_vectordb.py init-sample`
- **API errors**: Check your `.env` file has valid `OPENAI_API_KEY`

### **For Help:**
- Check the conversation examples above
- Use the vector database CLI tools for testing
- Review the project structure for customization

---

**Your complete HR hiring workflow is now ready for production use!** 🚀
