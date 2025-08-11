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
from advancpdf import Advanced
from RAG.RAG import Do_RAG

load_dotenv()
context_gloval = " "

@tool
def get_body(a: str) -> str:
    """gets the body of a url"""
    global context_gloval
    print(a)
    sys.exit(0)
    resp = requests.get(a)
    resp.raise_for_status()  # raise error if request fails

    soup = BeautifulSoup(resp.text, "html.parser")
    body = soup.body.get_text()
    context_gloval = context_gloval + body
    return body 

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
def get_150(url: str) -> str:
    """Returns first 150 words of a pdf"""
    all_words = []
    num_words_to_get = 150

    try:
       
        response = requests.get(url, timeout=15)
        response.raise_for_status() 
     
        pdf_stream = BytesIO(response.content)
        with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
        
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    all_words.extend(page_text.split())
                
                if len(all_words) >= num_words_to_get:
                    break
    
    except requests.exceptions.RequestException as e:
        return f"Error: Could not download the file from the URL. {e}"
    except Exception as e:
        return f"Error: Could not process the PDF file. {e}"

    return " ".join(all_words[:num_words_to_get])


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


async def PDFchoose(request) -> str:

    OpenAI_key = os.getenv("OPENAI_API_KEY")
    print(OpenAI_key)


    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0,openai_api_key=OpenAI_key)


    tools = [get_body, get_pdf, get_150, perform_curl]


    prompt = ChatPromptTemplate.from_messages([
        ("system", "You deal with PDFs, whenever a pdf link is sent to you, you get the first 150 words, if the first 150 words contain any mention of having a task or goal you have to get the complete body of it and return only the steps mentioned and nothing else, otherwise say not advanced"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


    agent = create_openai_tools_agent(llm, tools, prompt)


    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)



    # query = "What is the secret token of this url?, https://register.hackrx.in/utils/get-secret-token?hackTeam=1484"
    query = request.documents
    response = agent_executor.invoke({
        "input": query
    })
    if "not advanced" in response["output"]:
        answer = await Do_RAG(request)
        return answer
    else:
        answer = Advanced(request, response["output"])
        return answer
    

    



