"""
Document parsing service for extracting text from various file formats
"""

import re
from typing import List
from pathlib import Path


class DocumentParser:
    def __init__(self):
        pass
    
    def parse_document(self, file_path: Path, file_extension: str) -> str:
        """Parse document based on file type"""
        
        if file_extension == '.txt':
            return self._parse_txt(file_path)
        elif file_extension == '.md':
            return self._parse_markdown(file_path)
        elif file_extension == '.pdf':
            return self._parse_pdf(file_path)
        elif file_extension == '.docx':
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _parse_txt(self, file_path: Path) -> str:
        """Parse plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_markdown(self, file_path: Path) -> str:
        """Parse Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean up markdown formatting for better AI processing
        # Remove excessive newlines and format headers
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)
        
        return content
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file - simplified implementation"""
        try:
            # This is a simplified implementation
            # In production, you'd use libraries like PyPDF2, pdfplumber, or pymupdf
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            return self._clean_extracted_text(text)
        except ImportError:
            # Fallback if PyPDF2 not available
            return "PDF parsing requires PyPDF2 library. Please install it or upload as text file."
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def _parse_docx(self, file_path: Path) -> str:
        """Parse Word document - simplified implementation"""
        try:
            # This is a simplified implementation
            # In production, you'd use libraries like python-docx
            import docx
            
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._clean_extracted_text(text)
        except ImportError:
            # Fallback if python-docx not available
            return "Word document parsing requires python-docx library. Please install it or upload as text file."
        except Exception as e:
            raise ValueError(f"Failed to parse Word document: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def chunk_text(self, text: str, max_chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """
        Split large text into smaller chunks for better embedding and retrieval
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Start new chunk with overlap from previous chunk
                    if overlap > 0 and len(current_chunk) > overlap:
                        overlap_text = current_chunk[-overlap:]
                        current_chunk = overlap_text + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    # Single sentence is too long, split it
                    chunks.append(sentence[:max_chunk_size])
                    current_chunk = sentence[max_chunk_size:]
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_metadata(self, file_path: Path, file_extension: str) -> dict:
        """Extract metadata from document"""
        metadata = {
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_extension
        }
        
        # Add format-specific metadata
        if file_extension == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    metadata.update({
                        "pages": len(reader.pages),
                        "title": reader.metadata.get("/Title", "") if reader.metadata else "",
                        "author": reader.metadata.get("/Author", "") if reader.metadata else ""
                    })
            except:
                pass
        
        return metadata