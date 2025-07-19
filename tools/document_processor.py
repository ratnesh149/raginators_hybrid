"""
Document Processing Tools for Vector Database
Handles PDF, DOCX, and text file processing for HR documents
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Optional imports - will work without these if not installed
try:
    import PyPDF2
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from services.vector_db import get_vector_db

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process various document types for vector database storage"""
    
    def __init__(self):
        self.vector_db = get_vector_db()
        self.supported_extensions = ['.txt', '.md']
        
        if PDF_AVAILABLE:
            self.supported_extensions.extend(['.pdf'])
        if DOCX_AVAILABLE:
            self.supported_extensions.extend(['.docx', '.doc'])
    
    def process_text_file(self, file_path: str) -> str:
        """Process plain text or markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def process_pdf_file(self, file_path: str) -> str:
        """Process PDF files"""
        if not PDF_AVAILABLE:
            logger.warning("PDF processing not available. Install pypdf to enable.")
            return ""
        
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            return ""
    
    def process_docx_file(self, file_path: str) -> str:
        """Process DOCX files"""
        if not DOCX_AVAILABLE:
            logger.warning("DOCX processing not available. Install python-docx to enable.")
            return ""
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX file {file_path}: {e}")
            return ""
    
    def process_file(self, file_path: str) -> str:
        """Process a file based on its extension"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension in ['.txt', '.md']:
            return self.process_text_file(str(file_path))
        elif extension == '.pdf':
            return self.process_pdf_file(str(file_path))
        elif extension in ['.docx', '.doc']:
            return self.process_docx_file(str(file_path))
        else:
            logger.warning(f"Unsupported file type: {extension}")
            return ""
    
    def add_job_description_from_file(self, file_path: str, job_title: str, metadata: Dict[str, Any] = None):
        """Add job description from file to vector database"""
        content = self.process_file(file_path)
        if content:
            self.vector_db.add_job_description(job_title, content, metadata)
            logger.info(f"Added job description from {file_path}")
        else:
            logger.error(f"Failed to process file {file_path}")
    
    def add_resume_from_file(self, file_path: str, candidate_name: str, metadata: Dict[str, Any] = None):
        """Add resume from file to vector database"""
        content = self.process_file(file_path)
        if content:
            self.vector_db.add_resume(candidate_name, content, metadata)
            logger.info(f"Added resume from {file_path}")
        else:
            logger.error(f"Failed to process file {file_path}")
    
    def add_hr_policy_from_file(self, file_path: str, policy_name: str, metadata: Dict[str, Any] = None):
        """Add HR policy from file to vector database"""
        content = self.process_file(file_path)
        if content:
            self.vector_db.add_hr_policy(policy_name, content, metadata)
            logger.info(f"Added HR policy from {file_path}")
        else:
            logger.error(f"Failed to process file {file_path}")
    
    def bulk_process_directory(self, directory_path: str, document_type: str = "auto"):
        """Process all supported files in a directory"""
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory {directory_path} does not exist")
            return
        
        processed_count = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    file_name = file_path.stem
                    
                    if document_type == "job_descriptions" or (document_type == "auto" and "job" in file_name.lower()):
                        self.add_job_description_from_file(str(file_path), file_name)
                    elif document_type == "resumes" or (document_type == "auto" and "resume" in file_name.lower()):
                        self.add_resume_from_file(str(file_path), file_name)
                    elif document_type == "hr_policies" or (document_type == "auto" and "policy" in file_name.lower()):
                        self.add_hr_policy_from_file(str(file_path), file_name)
                    else:
                        # Default to HR policy for unknown types
                        self.add_hr_policy_from_file(str(file_path), file_name)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Processed {processed_count} files from {directory_path}")

def initialize_sample_data():
    """Initialize the vector database with sample data"""
    vector_db = get_vector_db()
    
    # Add sample data if the database is empty
    try:
        # Check if we have any data
        test_results = vector_db.search_similar_jobs("test", n_results=1)
        if not test_results:
            logger.info("Initializing vector database with sample data...")
            vector_db.add_sample_data()
            logger.info("Sample data added successfully")
        else:
            logger.info("Vector database already contains data")
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")

# Global processor instance
document_processor = DocumentProcessor()

if __name__ == "__main__":
    # Initialize sample data when run directly
    initialize_sample_data()
