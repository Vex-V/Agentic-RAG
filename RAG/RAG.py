from RAG.retriever import get_relevant_chunks
from RAG.model_openai import async_ask_openai
import asyncio
from typing import List



async def get_openai_responses_concurrently(questions: List[str], chunks: dict) -> List[str]:
    """Gathers all API call tasks and runs them in parallel."""
    tasks = []
    for q in questions:
        context = chunks.get(q, "")
        
        task = asyncio.create_task(async_ask_openai(context, q))
        tasks.append(task)
        
    results = await asyncio.gather(*tasks)
    final_answers = [res.strip() if res else "No answer found" for res in results]
    return final_answers

async def Do_RAG(request):
    loop = asyncio.get_running_loop()
    chunks = await loop.run_in_executor(None, get_relevant_chunks, request.documents, request.questions)
    
    responses = await get_openai_responses_concurrently(request.questions, chunks)
    return responses