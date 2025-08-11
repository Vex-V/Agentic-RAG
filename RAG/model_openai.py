import openai


client = openai.AsyncOpenAI(api_key="")

async def async_ask_openai(context: str, question: str) -> str:

  
    system_prompt = """
        - Try to keep it below 50 words
        - quote verbatim as much as possible, if present, try to mention numbers from the context
        - Do NOT add explanations.
        - Answer only from the context, if not there, reply not in context
        - if an answer is not in english, translate it to english, ignore otherwise
       
    """

    
    user_prompt = f"""
Context:
{context}

Question:
{question}
"""

    try:
        
        chat_completion = await client.chat.completions.create(
            
            model="gpt-4.1-nano", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
       
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"An error occurred for question '{question}': {e}")
       


        return "Error processing request."
