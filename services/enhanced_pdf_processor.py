#!/usr/bin/env python3
"""
Enhanced PDF Processing with Multiple Fallbacks
Hybrid solution combining best PDF extraction tools
"""

import os
import logging
from typing import Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFProcessor:
    """Multi-processor PDF extraction with fallbacks"""
    
    def __init__(self):
        self.processors = []
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize available PDF processors in order of preference"""
        
        # Processor 1: pdfplumber (best for resumes)
        try:
            import pdfplumber
            self.processors.append(('pdfplumber', self._extract_with_pdfplumber))
            logger.info("✅ pdfplumber processor available")
        except ImportError:
            logger.warning("❌ pdfplumber not available")
        
        # Processor 2: PyMuPDF (fast and reliable)
        try:
            import fitz  # pymupdf
            self.processors.append(('pymupdf', self._extract_with_pymupdf))
            logger.info("✅ PyMuPDF processor available")
        except ImportError:
            logger.warning("❌ PyMuPDF not available")
        
        # Processor 3: PyPDF2 (fallback)
        try:
            from PyPDF2 import PdfReader
            self.processors.append(('pypdf2', self._extract_with_pypdf2))
            logger.info("✅ PyPDF2 processor available")
        except ImportError:
            logger.warning("❌ PyPDF2 not available")
        
        if not self.processors:
            raise RuntimeError("No PDF processors available! Install pdfplumber, pymupdf, or PyPDF2")
    
    def extract_resume_content(self, pdf_path: str) -> str:
        """
        Extract content from PDF using multiple processors with fallbacks
        Returns the full resume text as a single string (no chunking)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        last_error = None
        
        for processor_name, processor_func in self.processors:
            try:
                logger.info(f"🔄 Trying {processor_name} for {os.path.basename(pdf_path)}")
                content = processor_func(pdf_path)
                
                if self._validate_content(content):
                    logger.info(f"✅ {processor_name} succeeded - {len(content)} characters extracted")
                    return self._clean_text(content)
                else:
                    logger.warning(f"⚠️  {processor_name} extracted invalid content")
                    
            except Exception as e:
                logger.warning(f"❌ {processor_name} failed: {str(e)}")
                last_error = e
                continue
        
        # All processors failed
        raise Exception(f"All PDF processors failed. Last error: {last_error}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF"""
        import fitz
        
        text = ""
        doc = fitz.open(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        
        doc.close()
        return text
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        from PyPDF2 import PdfReader
        
        text = ""
        reader = PdfReader(pdf_path)
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return text
    
    def _validate_content(self, content: str) -> bool:
        """Validate that extracted content is meaningful"""
        if not content or len(content.strip()) < 50:
            return False
        
        # Check for common resume indicators
        resume_indicators = [
            'experience', 'education', 'skills', 'work', 'employment',
            '@', 'email', 'phone', 'contact', 'resume', 'cv'
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in resume_indicators if indicator in content_lower)
        
        return indicator_count >= 2  # At least 2 resume indicators
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        return cleaned_text

# Global instance for easy import
enhanced_pdf_processor = EnhancedPDFProcessor()

def extract_pdf_content(pdf_path: str) -> str:
    """Convenience function for PDF extraction"""
    return enhanced_pdf_processor.extract_resume_content(pdf_path)

if __name__ == "__main__":
    # Test the processor
    import sys
    
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        try:
            content = extract_pdf_content(test_pdf)
            print(f"✅ Extracted {len(content)} characters")
            print("📄 First 200 characters:")
            print(content[:200])
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Usage: python enhanced_pdf_processor.py <pdf_file>")
