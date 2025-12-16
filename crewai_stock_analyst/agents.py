from crewai import Agent,LLM
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("openai_api_key")

llm = LLM(
    model="gpt-4o-mini",   # 👈 correct model name here
    api_key=api_key
)

resercher_agent=Agent(role='Researcher agent',
goal='find accurate and useful information on the user query',
backstory='you are an expert resercher',llm=llm,verbose=True)

write_agent=Agent(role='writer agent',
goal="Create clear and concise summaries from research notes",
backstory="You are a clear communicator who turns complex info into simple explanations.",llm=llm
,verbose=True)