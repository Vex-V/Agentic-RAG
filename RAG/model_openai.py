import openai


client = openai.AsyncOpenAI(api_key="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")

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