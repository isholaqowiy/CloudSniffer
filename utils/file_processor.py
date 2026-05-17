import os
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

class FileProcessor:
    @staticmethod
    def extract_text(file_path: str, extension: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Target resolution execution path mismatch.")
            
        # File sizing security limits check (max 5MB file processing)
        if os.path.getsize(file_path) > 5 * 1024 * 1024:
            raise ValueError("Target entity out of premium processing sizing limits bounds.")

        ext = extension.lower().strip(".")
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
                
        elif ext == "pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_idx in range(len(reader.pages)):
                    page_content = reader.pages[page_idx].extract_text()
                    if page_content:
                        text += page_content + "\n"
            return text.strip()
            
        elif ext == "docx":
            doc = docx.Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return "\n".join(full_text).strip()
            
        else:
            raise ValueError(f"Unsupported file extension context tracking: .{ext}")
