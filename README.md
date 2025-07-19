# 🧠 Agentic HR Assistant

An intelligent, multi-agent AI application that helps HR professionals plan and execute startup hiring processes — powered by LangGraph, vector databases, and function-based routing.

## 🚀 Overview

This project demonstrates how to build a multi-agent, memory-aware AI assistant using LangGraph, LangChain, vector databases, and OpenAI's GPT APIs.

It allows HR users to:

- Plan and execute hiring processes
- Generate job descriptions with similar job insights
- Create hiring checklists with relevant interview questions
- Search and match candidates against job requirements
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

The system now includes a comprehensive vector database that stores and retrieves:

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

## 🧠 Agents

### 👥 1. Chatbot Agent (Interface)
- Acts as the main interface with the user
- Asks clarifying questions about roles, budget, skills, timeline
- Routes requests to other agents

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

## 🛠️ How to Run

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set up .env
```
OPENAI_API_KEY=your_api_key
```

3. Initialize vector database (optional - sample data will be added automatically)
```bash
python manage_vectordb.py init-sample
```

4. Run the assistant
```bash
python run.py
```

5. Chat! Type prompts like:
```
I want to hire a frontend developer
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
| Routing | Rule-based chatbot | Meant to reduce back-and-forth between agents |
| Memory | MemorySaver() | Simple in-memory state retention for single sessions |
| State | Based on MessagesState | Leverages LangGraph's built-in message tracking |
| Vector DB | ChromaDB | Local, persistent, easy to integrate |
| Embeddings | Sentence Transformers | Fast, local, good quality embeddings |
| Output | Markdown + CLI | Simple developer-facing display for easy testing |
| Agent Flow | One agent at a time | Avoids noisy overlap and redundant messages |

## 📈 With More Time, We'd Improve...

- ✅ ~~Proper conditional routing~~ ✅ COMPLETED
  - Implement router-based branching so only the correct agent is invoked each turn
- ✅ ~~Vector Database Integration~~ ✅ COMPLETED
  - Add document storage, similarity search, and knowledge retrieval
- 📬 Tool Integration (Email, Resume Parser)
  - Add simulated email writer, advanced resume screening, interview calendar tool
- 🔐 Persistent user memory
  - Swap out in-memory state for file-based or vector memory for long-term recall
- 🌐 Frontend UI (React or Streamlit)
  - Move from CLI to a professional web UI with role selection, forms, and message threading
- 👥 Multi-role hiring flow
  - Enable tracking multiple open roles at once (e.g., GenAI intern + DevOps lead)
- 🧪 Unit tests & CI
  - Add agent-specific tests and CI/CD deployment scripts
- 🔍 Advanced Search Features
  - Faceted search, filters, ranking algorithms
- 📈 Analytics Dashboard
  - Hiring metrics, candidate pipeline tracking, success rates

## 📂 Project Structure

```
agentic-hr-assistant/
├── agents/
│   ├── jd_agent.py          # Job description generation agent (enhanced)
│   └── checklist_agent.py   # Hiring checklist generation agent
├── graph/
│   └── stategraph.py        # LangGraph graph setup + memory
├── nodes/
│   ├── chatbot.py           # Interface agent
│   ├── agentnodes.py        # JD + checklist agents (enhanced)
│   └── human.py             # Fallback handler
├── services/
│   └── vector_db.py         # Vector database service
├── tools/
│   ├── google_search.py     # Google search integration
│   ├── vector_tools.py      # Vector database tools for agents
│   └── document_processor.py # Document processing utilities
├── app.py                   # Streamlit web interface
├── llm_init.py             # LLM initialization and configuration
├── requirements.txt        # Project dependencies (updated)
├── run.py                  # CLI runtime loop (enhanced)
├── manage_vectordb.py      # Vector database management CLI
├── stateclass.py           # Defines shared state between agents
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## 🎯 Vector Database Use Cases

1. **Job Description Enhancement**: Find similar roles to improve JD quality
2. **Candidate Matching**: Search resumes for skills and experience alignment  
3. **Interview Preparation**: Get relevant questions for specific roles
4. **Policy Compliance**: Ensure hiring practices follow company guidelines
5. **Knowledge Retention**: Build institutional memory of hiring decisions
6. **Template Library**: Maintain reusable hiring assets and templates
