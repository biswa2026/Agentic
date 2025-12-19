from crewai import Agent, LLM
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("openai_api_key")

llm = LLM(
    model="gpt-4o-mini",   # 👈 correct model name here
    api_key=api_key)


# Classifier Agent
classifier_agent = Agent(
    role="Ticket Classifier",
    goal="Analyze incoming support tickets and classify them by topic and priority {ticket}.",
    backstory="Expert in customer queries with strong classification skills.",
    llm=llm,
    verbose=True
)

# Responder Agent
responder_agent = Agent(
    role="Response Generator",
    goal="Draft appropriate responses for classified {ticket}.",
    backstory="Skilled in customer communication and problem-solving.",
    llm=llm,
    verbose=True
)

# Escalation Agent
escalation_agent = Agent(
    role="Escalation Specialist",
    goal="Identify tickets that require human intervention and prepare escalation notes {ticket}.",
    backstory="Experienced in triaging complex customer support issues.",
    llm=llm,
    verbose=True
)
mail_agent=Agent(role='mail agent',
                  goal='you are a mail agents who transform ticket insights and sends mail in html format',
                   backstory="Expert in professional communication and HTML email formatting.",
                   llm=llm
                  )