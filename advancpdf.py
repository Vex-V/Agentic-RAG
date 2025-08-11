from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import sys
from io import BytesIO
import fitz


load_dotenv()
context_gloval = " "



@tool
def get_pdf(url: str) -> str:
    """Gets the body text of a PDF from a URL."""
    global context_gloval

    response = requests.get(url)
    pdf_data = BytesIO(response.content)
    doc = fitz.open("pdf", pdf_data.read())
    text = ""
    for page in doc:
        text += page.get_text()
    context_gloval = context_gloval + text
    return text
 

@tool
def perform_curl(url: str) -> str:
    """
    Makes an API call to a URL and returns the raw response text.
    """
    global context_gloval

    response = requests.get(url)
    text = response.text.strip()
    context_gloval = context_gloval + text

    return text


def Advanced(request,instrucs : str) -> str:

    OpenAI_key = os.getenv("OPENAI_API_KEY")
    print(OpenAI_key)


    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0,openai_api_key=OpenAI_key)


    tools = [get_pdf,perform_curl]


    prompt = ChatPromptTemplate.from_messages([
        ("system", "You deal with PDFs, you will be provided with an instruction set and a link to a PDF, get the PDF body and follow the instructions given step by step to retrieve the answer to the question, keep the answer brief"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


    agent = create_openai_tools_agent(llm, tools, prompt)


    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)



    
    query = str(request.documents) + instrucs
    response = agent_executor.invoke({
        "input": query
    })



    return response["output"]
    


