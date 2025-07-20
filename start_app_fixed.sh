#!/bin/bash

# Fixed Startup script for Raginators-Hybrid App with Enhanced UI and Advanced Candidate Evaluation

echo "🚀 Starting Raginators-Hybrid App with Enhanced UI & Advanced Evaluation"
echo "========================================================================"

# Change to the app directory
cd /home/ratnesh/raginators-hybrid

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv-hybrid/bin/activate

# Install missing dependencies
echo "📦 Installing/updating dependencies..."
pip install langgraph langchain-openai langchain-community scikit-learn numpy pandas

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."
python3 -c "
import sys
missing_deps = []

try:
    import streamlit
    print('✅ streamlit available')
except ImportError:
    missing_deps.append('streamlit')

try:
    import sklearn
    print('✅ scikit-learn available')
except ImportError:
    missing_deps.append('scikit-learn')

try:
    import numpy
    print('✅ numpy available')
except ImportError:
    missing_deps.append('numpy')

try:
    from services.candidate_evaluator import candidate_evaluator
    print('✅ candidate_evaluator available')
except ImportError as e:
    print(f'❌ candidate_evaluator error: {e}')
    missing_deps.append('candidate_evaluator')

try:
    from tools.candidate_evaluation import candidate_evaluation_tool
    print('✅ candidate_evaluation_tool available')
except ImportError as e:
    print(f'❌ candidate_evaluation_tool error: {e}')
    missing_deps.append('candidate_evaluation_tool')

try:
    from graph.stategraph import graph
    print('✅ graph available')
except ImportError as e:
    print(f'❌ graph error: {e}')
    missing_deps.append('graph')

if missing_deps:
    print(f'❌ Missing dependencies: {missing_deps}')
    sys.exit(1)
else:
    print('✅ All dependencies are available')
"

if [ $? -ne 0 ]; then
    echo "❌ Dependency check failed. Please check the error messages above."
    exit 1
fi

# Test the core functionality
echo "🧪 Testing core functionality..."
python3 -c "
from services.vector_db import get_vector_db
vector_db = get_vector_db()
results = vector_db.search_candidates('React developer', 1)
if results:
    print('✅ Vector database is working')
    print(f'   Found candidate: {results[0].get(\"metadata\", {}).get(\"candidate_name\", \"Unknown\")}')
else:
    print('⚠️  No candidates found in database')
"

# Test app syntax
echo "🔍 Testing app syntax..."
python3 -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "✅ App syntax check passed"
else
    echo "❌ App syntax check failed"
    exit 1
fi

echo ""
echo "🌟 **ENHANCED FEATURES READY:**"
echo ""
echo "📊 **ENHANCED UI FEATURES:**"
echo "   ✅ Dual View Modes: Detailed Cards & Table Summary"
echo "   ✅ Smart Candidate Categorization (Selected/Rejected/Not Evaluated)"
echo "   ✅ Clear Reason Columns with detailed justifications"
echo "   ✅ Individual & Bulk Resume Download options"
echo "   ✅ Professional evaluation scoring display"
echo "   ✅ Expandable sections for detailed analysis"
echo ""
echo "🎯 **ADVANCED EVALUATION SYSTEM:**"
echo "   ✅ 60% accuracy threshold for automatic selection"
echo "   ✅ Multi-dimensional scoring (semantic, skills, experience)"
echo "   ✅ Detailed justification for selection/rejection"
echo "   ✅ Professional HR-ready output"
echo ""

echo "🖥️  Starting Streamlit app..."
echo "📱 The app will be available at: http://localhost:8501"
echo ""
echo "💡 **How to use the enhanced features:**"
echo ""
echo "   1️⃣  Fill out the job requirements form"
echo "   2️⃣  Click 'Find Candidates'"
echo "   3️⃣  ✨ Advanced evaluation automatically runs"
echo "   4️⃣  Choose your view mode:"
echo "       📋 Detailed Cards View - Rich candidate cards with full details"
echo "       📊 Table Summary View - Compact overview of all candidates"
echo "   5️⃣  Review candidates by category:"
echo "       ✅ Selected (60%+ match) - Highlighted with reasons"
echo "       ❌ Rejected (<60% match) - Clear gap analysis"
echo "       📋 Not Evaluated - Legacy candidates"
echo "   6️⃣  Download resumes:"
echo "       📄 Individual downloads per candidate"
echo "       📦 Bulk download all resumes (ZIP)"
echo "       ✅ Download selected candidates only (ZIP)"
echo "       📊 Export candidate data (CSV)"
echo ""
echo "🎉 **ALL SHORTLISTED CANDIDATES ARE NOW FULLY VISIBLE!**"
echo "    Every candidate is displayed with clear reasons and download options"
echo ""
echo "🚀 **UI FIXES APPLIED:**"
echo "   ✅ Fixed missing dependencies (langgraph, langchain-openai, langchain-community)"
echo "   ✅ Added error handling for score formatting"
echo "   ✅ Simplified dataframe display for compatibility"
echo "   ✅ Added comprehensive dependency checking"
echo ""

# Start the Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
