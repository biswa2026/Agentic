import os
import openai

# ------------------ Set API key ------------------
openai.api_key = os.getenv("openai_api_key")

# ------------------ ModelSettings — tiny container ------------------
class ModelSettings:
    def __init__(self, max_tokens=512):
        self.max_tokens = max_tokens

# ------------------ function_tool decorator ------------------
def function_tool(func):
    return func

# ------------------ SQLiteSession placeholder ------------------
class SQLiteSession:
    def __init__(self, name): pass
    def close(self): pass

# ------------------ Agent ------------------
class Agent:
    def __init__(self, name, instructions, tools=None, handoffs=None, model="text-davinci-003", model_settings=None):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
        self.model_settings = model_settings or ModelSettings()

# ------------------ Runner ------------------
class Runner:
    @staticmethod
    def run_sync(agent, user_input, session=None, max_turns=3):
        """
        Synchronous runner using old OpenAI API (0.28.1)
        """

        # Find the retrieval tool (if any)
        retrieval_tool = next((t for t in agent.tools if t.__name__ == "retrieve_context"), None)

        # Initial system + user message
        messages = [
            {"role": "system", "content": agent.instructions},
            {"role": "user", "content": user_input}
        ]

        # GPT call using old API
        response = openai.Completion.create(
            engine=agent.model,
            prompt=f"{agent.instructions}\n\nUser: {user_input}\nAssistant:",
            max_tokens=agent.model_settings.max_tokens
        )
        answer = response.choices[0].text.strip()

        # Use retrieval tool if answer is weak or NO_CONTEXT_FOUND
        if retrieval_tool and ("NO_CONTEXT_FOUND" in answer or len(answer) < 50):
            context = retrieval_tool(user_input)
            augmented_prompt = f"{agent.instructions}\n\nContext:\n{context}\n\nUser: {user_input}\nAssistant:"
            final = openai.Completion.create(
                engine=agent.model,
                prompt=augmented_prompt,
                max_tokens=agent.model_settings.max_tokens
            )
            answer = final.choices[0].text.strip()

        # Fake Result object to mimic your previous usage
        class Result:
            final_output = answer

        return Result()
