import requests
from io import BytesIO
import fitz  # PyMuPDF
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


def EandCL(url, chunk_size, overlap):
    response = requests.get(url)
    pdf_data = BytesIO(response.content)
    doc = fitz.open("pdf", pdf_data.read())
    chunks = []
    buffer = []
    for page in doc:
        # Use a regular expression to split by one or more whitespace characters
        words = re.split(r'\s+', page.get_text().strip())
        # Filter out any empty strings that might remain
        words = [word for word in words if word]
        buffer.extend(words)
        i = 0
        while i < len(buffer):
            chunk = buffer[i:i + chunk_size]
            if not chunk:
                break
            chunks.append(" ".join(chunk))
            i += chunk_size - overlap
        buffer = buffer[-overlap:]
    return chunks


def EandCR(url, chunk_size, chunk_overlap):
    try:
        
        response = requests.get(url)
        response.raise_for_status()
        pdf_data = BytesIO(response.content)
        doc = fitz.open(stream=pdf_data, filetype="pdf")

        full_text = "".join(page.get_text() for page in doc)
        doc.close()

        if not full_text.strip():
            return []

        # Pre-process the text to remove large blanks and count meaningful characters
        cleaned_text = re.sub(r'\n\s*\n', '\n', full_text)  # Replace multiple newlines with one
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip() # Replace all whitespace sequences with a single space

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_text(cleaned_text)
        return chunks

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def is_pdf(url): 
    if 'PDF' in url:
        return True
    return False