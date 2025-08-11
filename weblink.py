from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup


load_dotenv()


@tool
def get_body(a: str) -> str:
    """gets the body of a url"""
    resp = requests.get(a)
    resp.raise_for_status()  # raise error if request fails

    soup = BeautifulSoup(resp.text, "html.parser")
    body = soup.body.get_text()
    
    return body 
    

def Weblink(request)-> str:

    OpenAI_key = os.getenv("OPENAI_API_KEY")
    print(OpenAI_key)

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0,openai_api_key=OpenAI_key)


    tools = [get_body]


    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are given a web link, get the contents and return the answer based on the question"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


    agent = create_openai_tools_agent(llm, tools, prompt)


    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    

    query = request
    response = agent_executor.invoke({
        "input": query
    })
    return response["output"]

