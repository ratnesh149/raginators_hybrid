import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

# Import hybrid components
from .enhanced_pdf_processor import enhanced_pdf_processor
from .local_metadata_extractor import local_metadata_extractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridVectorDB:
    """
    Hybrid Vector Database with No-Chunking Strategy
    Uses unique candidate IDs to eliminate duplicates
    """
    
    def __init__(self, persist_directory: str = "./hybrid_chroma_db"):
        """Initialize hybrid vector database"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create collections
        self.collections = {}
        self._initialize_collections()
        
        logger.info(f"✅ Hybrid Vector Database initialized at {persist_directory}")
    
    def _initialize_collections(self):
        """Initialize ChromaDB collections"""
        
        # Candidates collection (no chunking - whole resumes)
        self.collections["candidates"] = self.client.get_or_create_collection(
            name="candidates_hybrid",
            metadata={"description": "Candidate resumes - no chunking, unique IDs"}
        )
        
        # Job descriptions collection
        self.collections["job_descriptions"] = self.client.get_or_create_collection(
            name="job_descriptions_hybrid",
            metadata={"description": "Job descriptions"}
        )
        
        # Interview questions collection
        self.collections["interview_questions"] = self.client.get_or_create_collection(
            name="interview_questions_hybrid",
            metadata={"description": "Interview questions"}
        )
        
        logger.info("✅ Collections initialized")
    
    def generate_unique_id(self, pdf_content: str, metadata: Dict[str, Any], pdf_filename: str) -> str:
        """Generate unique candidate ID"""
        import hashlib
        
        # Create unique ID from content + metadata
        content_hash = hashlib.md5(pdf_content.encode()).hexdigest()[:8]
        email = metadata.get('email', '')
        phone = metadata.get('phone', '')
        meta_hash = hashlib.md5(f"{email}{phone}".encode()).hexdigest()[:4]
        file_hash = hashlib.md5(pdf_filename.encode()).hexdigest()[:4]
        
        return f"candidate_{content_hash}_{meta_hash}_{file_hash}"
    
    def add_resume(self, candidate_name: str, resume_text: str, metadata: Dict[str, Any]):
        """
        Add resume to vector database (NO CHUNKING)
        Each resume is stored as a single entry with unique ID
        """
        
        # Generate unique candidate ID
        pdf_filename = metadata.get('pdf_filename', 'unknown.pdf')
        unique_id = self.generate_unique_id(resume_text, metadata, pdf_filename)
        
        # Enhanced metadata with unique ID
        enhanced_metadata = {
            **metadata,
            'unique_id': unique_id,
            'candidate_name': candidate_name,
            'processing_method': 'hybrid_no_chunking'
        }
        
        try:
            # Check if candidate already exists
            existing = self._get_candidate_by_id(unique_id)
            if existing:
                logger.info(f"🔄 Updating existing candidate: {candidate_name} ({unique_id})")
                self._update_candidate(unique_id, resume_text, enhanced_metadata)
            else:
                logger.info(f"➕ Adding new candidate: {candidate_name} ({unique_id})")
                self._add_new_candidate(unique_id, resume_text, enhanced_metadata)
                
        except Exception as e:
            logger.error(f"❌ Error adding resume for {candidate_name}: {e}")
            raise
    
    def _get_candidate_by_id(self, unique_id: str) -> Optional[Dict]:
        """Check if candidate already exists by unique ID"""
        try:
            results = self.collections["candidates"].get(
                ids=[unique_id],
                include=['metadatas', 'documents']
            )
            return results if results['ids'] else None
        except Exception:
            return None
    
    def _add_new_candidate(self, unique_id: str, resume_text: str, metadata: Dict[str, Any]):
        """Add new candidate to database"""
        self.collections["candidates"].add(
            documents=[resume_text],  # Whole resume, no chunking
            metadatas=[metadata],
            ids=[unique_id]
        )
    
    def _update_candidate(self, unique_id: str, resume_text: str, metadata: Dict[str, Any]):
        """Update existing candidate"""
        self.collections["candidates"].update(
            documents=[resume_text],
            metadatas=[metadata],
            ids=[unique_id]
        )
    
    def search_candidates(self, query: str, n_results: int = 10, 
                         filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search candidates with automatic deduplication
        Returns unique candidates only (no duplicates possible with unique IDs)
        """
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if filters:
                for key, value in filters.items():
                    if isinstance(value, dict) and '>=' in value:
                        # Handle numeric filters like experience_years >= 4
                        where_clause[key] = {"$gte": value['>=']}
                    else:
                        where_clause[key] = value
            
            # Search in candidates collection
            results = self.collections["candidates"].query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None
                    }
                    formatted_results.append(result)
            
            logger.info(f"🔍 Search for '{query}' returned {len(formatted_results)} unique candidates")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    def add_sample_data(self):
        """Add actual PDF resume data to the vector database (NO CHUNKING)"""
        
        pdf_files = []
        sample_resumes_path = Path("sample_resumes")
        
        if not sample_resumes_path.exists():
            logger.warning("sample_resumes folder not found")
            return
        
        # Get all PDF files
        for pdf_file in sample_resumes_path.glob("*.pdf"):
            pdf_files.append(pdf_file)
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files in sample_resumes folder")
        
        # Process actual PDF files with NO CHUNKING
        processed_candidates = []
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"🔄 Processing {pdf_file.name}...")
                
                # Extract candidate name from filename
                filename = pdf_file.stem
                parts = filename.split('_')
                if len(parts) >= 4:
                    candidate_name = f"{parts[2]} {parts[3]}"
                else:
                    candidate_name = filename.replace('_', ' ').title()
                
                # Extract FULL content from PDF (no chunking)
                try:
                    resume_text = enhanced_pdf_processor.extract_resume_content(str(pdf_file))
                    
                    if not resume_text.strip():
                        logger.warning(f"⚠️  No text extracted from {pdf_file.name}")
                        continue
                        
                except Exception as pdf_error:
                    logger.warning(f"❌ Error reading PDF {pdf_file.name}: {pdf_error}")
                    continue
                
                # Extract metadata using local extractor
                metadata_obj = local_metadata_extractor.extract_metadata(resume_text)
                
                # Convert to dict with ChromaDB-compatible types (no lists)
                metadata_dict = {
                    'candidate_name': candidate_name,
                    'experience_years': float(metadata_obj.experience_years),
                    'skills': ', '.join(metadata_obj.skills) if metadata_obj.skills else '',
                    'domains': ', '.join(metadata_obj.domains) if metadata_obj.domains else '',
                    'email': metadata_obj.email or '',
                    'phone': metadata_obj.phone or '',
                    'education_level': metadata_obj.education_level or '',
                    'certifications': ', '.join(metadata_obj.certifications) if metadata_obj.certifications else '',
                    'languages': ', '.join(metadata_obj.languages) if metadata_obj.languages else '',
                    'location': metadata_obj.location or '',
                    'confidence_score': float(metadata_obj.confidence_score),
                    'extraction_method': metadata_obj.extraction_method,
                    'pdf_file_path': str(pdf_file),
                    'pdf_filename': pdf_file.name,
                    'file_size': int(pdf_file.stat().st_size)
                }
                
                # Add resume with NO CHUNKING (whole resume as single entry)
                self.add_resume(candidate_name, resume_text, metadata_dict)
                processed_candidates.append(candidate_name)
                
            except Exception as e:
                logger.warning(f"❌ Error processing {pdf_file.name}: {e}")
        
        logger.info(f"✅ Processed {len(processed_candidates)} actual PDF resumes with NO CHUNKING")
        logger.info("✅ Added actual PDF data to hybrid vector database")

# Global instance
hybrid_vector_db = None

def get_vector_db() -> HybridVectorDB:
    """Get or create the global hybrid vector database instance"""
    global hybrid_vector_db
    if hybrid_vector_db is None:
        hybrid_vector_db = HybridVectorDB()
    return hybrid_vector_db
