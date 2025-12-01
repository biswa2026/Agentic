from agents import Agent, ModelSettings
from tools.retrieval import retrieve_context

qa_agent = Agent(
    name="Answer Engine",
    instructions=(
        "You are a helpful assistant answering questions based on retrieved context. "
        "Always cite sources when using context. Keep answers concise and accurate."
    ),
    tools=[retrieve_context],
    model="gpt-4o-mini",
    model_settings=ModelSettings(max_tokens=512)
)