#!/usr/bin/env python3
"""
Local Metadata Extractor
Enhanced extraction using spaCy + regex patterns (no API calls needed)
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedMetadata:
    """Structured metadata extracted from resume"""
    candidate_name: str
    experience_years: float
    skills: List[str]
    domains: List[str]
    email: str
    phone: str
    education_level: str
    certifications: List[str]
    languages: List[str]
    location: str
    confidence_score: float
    extraction_method: str

class LocalMetadataExtractor:
    """Local metadata extraction using spaCy + enhanced regex patterns"""
    
    def __init__(self):
        self.nlp = None
        self._initialize_nlp()
        self._initialize_patterns()
    
    def _initialize_nlp(self):
        """Initialize spaCy NLP model"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️  spaCy not available: {e}")
            self.nlp = None
    
    def _initialize_patterns(self):
        """Initialize regex patterns for extraction"""
        
        # Email patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Phone patterns
        self.phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+?([0-9]{1,3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        ]
        
        # Experience patterns (enhanced)
        self.experience_patterns = [
            r'(\d+)[\+\-\s]*years?\s*of\s*(progressive\s*)?experience',
            r'with\s+(\d+)[\+\-\s]*years?\s*(of\s*)?experience',
            r'(\d+)[\+\-\s]*years?\s*(of\s*)?experience\s*in',
            r'experience[:\s]*(\d+)[\+\-\s]*years?',
            r'(\d+)[\+\-\s]*years?\s*in\s*(the\s*)?field',
            r'over\s+(\d+)[\+\-\s]*years?\s*of',
            r'more\s*than\s+(\d+)[\+\-\s]*years?'
        ]
        
        # Date range pattern for experience calculation
        self.date_pattern = r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|present|current|now)'
        
        # Skills keywords (comprehensive)
        self.skill_keywords = {
            'programming': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift',
                'TypeScript', 'PHP', 'Ruby', 'Scala', 'Kotlin', 'R', 'MATLAB'
            ],
            'web_frontend': [
                'React', 'Angular', 'Vue.js', 'HTML', 'CSS', 'SASS', 'LESS',
                'Bootstrap', 'Tailwind', 'jQuery', 'Redux', 'Next.js', 'Nuxt.js'
            ],
            'web_backend': [
                'Node.js', 'Django', 'Flask', 'Express', 'Spring', 'Laravel',
                'Rails', 'ASP.NET', 'FastAPI', 'Gin', 'Echo'
            ],
            'databases': [
                'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Oracle', 'SQLite', 'Cassandra', 'DynamoDB'
            ],
            'cloud': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
                'CloudFormation', 'Ansible', 'Jenkins', 'GitLab CI'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'AI', 'TensorFlow', 'PyTorch',
                'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter', 'Tableau', 'Power BI'
            ],
            'mobile': [
                'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic'
            ],
            'tools': [
                'Git', 'Linux', 'Unix', 'Bash', 'PowerShell', 'Vim', 'VS Code',
                'IntelliJ', 'Eclipse', 'Postman', 'Swagger'
            ]
        }
        
        # Education levels
        self.education_patterns = {
            'PhD': r'(ph\.?d|doctorate|doctoral)',
            'Masters': r'(master|m\.s\.|m\.a\.|mba|m\.eng)',
            'Bachelors': r'(bachelor|b\.s\.|b\.a\.|b\.eng|b\.tech)',
            'Associates': r'(associate|a\.s\.|a\.a\.)',
            'High School': r'(high\s*school|diploma|ged)'
        }
        
        # Certification patterns
        self.certification_patterns = [
            r'(aws|amazon)\s*(certified|certification)',
            r'(azure|microsoft)\s*(certified|certification)',
            r'(google|gcp)\s*(certified|certification)',
            r'(cisco|ccna|ccnp)',
            r'(pmp|project\s*management)',
            r'(scrum|agile)\s*(master|certified)',
            r'(cissp|security)',
            r'(cpa|certified\s*public\s*accountant)'
        ]
    
    def extract_metadata(self, resume_text: str) -> ExtractedMetadata:
        """Extract comprehensive metadata from resume text"""
        
        if not resume_text:
            return self._create_empty_metadata()
        
        # Extract basic information
        candidate_name = self._extract_name(resume_text)
        email = self._extract_email(resume_text)
        phone = self._extract_phone(resume_text)
        
        # Extract experience
        experience_years = self._extract_experience(resume_text)
        
        # Extract skills and domains
        skills, domains = self._extract_skills_and_domains(resume_text)
        
        # Extract education
        education_level = self._extract_education(resume_text)
        
        # Extract certifications
        certifications = self._extract_certifications(resume_text)
        
        # Extract languages
        languages = self._extract_languages(resume_text)
        
        # Extract location
        location = self._extract_location(resume_text)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            candidate_name, email, phone, experience_years, skills
        )
        
        return ExtractedMetadata(
            candidate_name=candidate_name,
            experience_years=experience_years,
            skills=skills,
            domains=domains,
            email=email,
            phone=phone,
            education_level=education_level,
            certifications=certifications,
            languages=languages,
            location=location,
            confidence_score=confidence_score,
            extraction_method="local_spacy_regex"
        )
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name using multiple strategies"""
        
        # Strategy 1: Use spaCy NER if available
        if self.nlp:
            try:
                doc = self.nlp(text[:500])  # First 500 chars for name
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                        return ent.text.strip()
            except Exception:
                pass
        
        # Strategy 2: Look for name patterns at the beginning
        lines = text.split('\n')[:5]  # First 5 lines
        
        for line in lines:
            line = line.strip()
            if not line or '@' in line or any(char.isdigit() for char in line):
                continue
            
            # Check if line looks like a name
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.isalpha() or '-' in word for word in words):
                return line
        
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        match = re.search(self.email_pattern, text, re.IGNORECASE)
        return match.group() if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        for pattern in self.phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return ""
    
    def _extract_experience(self, text: str) -> float:
        """Extract years of experience using multiple methods"""
        
        experience_years = 0.0
        
        # Method 1: Direct experience statements
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                for match in matches:
                    years = int(match[0]) if isinstance(match, tuple) else int(match)
                    experience_years = max(experience_years, years)
        
        # Method 2: Calculate from date ranges
        current_year = datetime.now().year
        date_matches = re.findall(self.date_pattern, text.lower())
        
        if date_matches:
            total_calculated = 0
            for start, end in date_matches:
                try:
                    start_year = int(start)
                    end_year = current_year if end in ['present', 'current', 'now'] else int(end)
                    
                    if start_year <= end_year <= current_year:
                        total_calculated += (end_year - start_year)
                except ValueError:
                    continue
            
            # Use calculated experience if reasonable (1-40 years)
            if 1 <= total_calculated <= 40:
                experience_years = max(experience_years, total_calculated)
        
        return min(experience_years, 50)  # Cap at 50 years
    
    def _extract_skills_and_domains(self, text: str) -> tuple:
        """Extract skills and categorize into domains"""
        
        found_skills = []
        domains = set()
        
        text_lower = text.lower()
        
        # Extract skills by category
        for domain, skills in self.skill_keywords.items():
            domain_skills = []
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
                    domain_skills.append(skill)
            
            if domain_skills:
                domains.add(domain.replace('_', ' ').title())
        
        return found_skills, list(domains)
    
    def _extract_education(self, text: str) -> str:
        """Extract highest education level"""
        
        text_lower = text.lower()
        
        # Check in order of highest to lowest
        for level, pattern in self.education_patterns.items():
            if re.search(pattern, text_lower):
                return level
        
        return ""
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        
        certifications = []
        text_lower = text.lower()
        
        for pattern in self.certification_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                cert = match if isinstance(match, str) else ' '.join(match)
                certifications.append(cert.title())
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract programming and spoken languages"""
        
        languages = []
        
        # Programming languages already covered in skills
        # Look for spoken languages
        language_patterns = [
            r'languages?[:\s]*([\w\s,]+)',
            r'fluent\s*in[:\s]*([\w\s,]+)',
            r'native[:\s]*([\w\s,]+)',
            r'bilingual[:\s]*([\w\s,]+)'
        ]
        
        for pattern in language_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                langs = [lang.strip().title() for lang in match.split(',')]
                languages.extend(langs)
        
        return list(set(languages))
    
    def _extract_location(self, text: str) -> str:
        """Extract location information"""
        
        # Look for location patterns
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
            r'location[:\s]*([A-Z][a-z\s,]+)',
            r'based\s*in[:\s]*([A-Z][a-z\s,]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _calculate_confidence(self, name: str, email: str, phone: str, 
                            experience: float, skills: List[str]) -> float:
        """Calculate confidence score for extracted metadata"""
        
        score = 0.0
        
        # Name confidence
        if name and name != "Unknown":
            score += 0.3
        
        # Contact info confidence
        if email:
            score += 0.2
        if phone:
            score += 0.1
        
        # Experience confidence
        if experience > 0:
            score += 0.2
        
        # Skills confidence
        if skills:
            score += min(0.2, len(skills) * 0.02)
        
        return min(score, 1.0)
    
    def _create_empty_metadata(self) -> ExtractedMetadata:
        """Create empty metadata structure"""
        return ExtractedMetadata(
            candidate_name="Unknown",
            experience_years=0.0,
            skills=[],
            domains=[],
            email="",
            phone="",
            education_level="",
            certifications=[],
            languages=[],
            location="",
            confidence_score=0.0,
            extraction_method="local_spacy_regex"
        )

# Global instance
local_metadata_extractor = LocalMetadataExtractor()

def extract_metadata(resume_text: str) -> Dict[str, Any]:
    """Convenience function to extract metadata and return as dict"""
    metadata = local_metadata_extractor.extract_metadata(resume_text)
    
    return {
        'candidate_name': metadata.candidate_name,
        'experience_years': metadata.experience_years,
        'skills': ', '.join(metadata.skills),
        'domains': metadata.domains,
        'email': metadata.email,
        'phone': metadata.phone,
        'education_level': metadata.education_level,
        'certifications': metadata.certifications,
        'languages': metadata.languages,
        'location': metadata.location,
        'confidence_score': metadata.confidence_score,
        'extraction_method': metadata.extraction_method
    }

if __name__ == "__main__":
    # Test the extractor
    test_resume = """
    John Smith
    john.smith@email.com | +1-555-123-4567 | New York, NY
    
    PROFESSIONAL SUMMARY
    Accomplished Software Engineer with 8 years of progressive experience in full-stack development.
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL
    
    EXPERIENCE
    Senior Software Engineer | TechCorp (2020 - Present)
    Software Engineer | StartupXYZ (2016 - 2020)
    
    EDUCATION
    Bachelor of Science in Computer Science
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    """
    
    print("🧪 Testing Local Metadata Extractor")
    print("=" * 50)
    
    metadata = extract_metadata(test_resume)
    
    for key, value in metadata.items():
        print(f"{key}: {value}")
