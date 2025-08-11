from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI, BackgroundTasks
import asyncio
from typing import List
import aiofiles
import time
from weblink import Weblink
from pdfchoose import PDFchoose
app = FastAPI()


class RAGRequest(BaseModel):
    documents: str  
    questions: List[str]


import requests

def is_url_pdf(url):
   
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()  
        content_type = response.headers.get('Content-Type', '').lower()
        return 'application/pdf' in content_type
    except requests.exceptions.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False



@app.post("/hackrx/run")
async def run_rag(request: RAGRequest, background_tasks: BackgroundTasks):
    check = (is_url_pdf(request.documents))
    
    if check == False:
        response = Weblink((request))
    
    elif check == True:
        response = await PDFchoose(request)

    return {"success": True, "answers": response}
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
