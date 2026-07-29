"""
ReAct agent with mem0

Overview:
A ReAct agent combines reasoning and action capabilities, making it versatile for tasks requiring both thought processes (reasoning) and interaction with tools or APIs (acting).
Mem0 as memory enhances these capabilities by allowing the agent to store and retrieve contextual information from past interactions.

Ref:
1. ReAct Agents with Memory: https://docs.mem0.ai/cookbooks/frameworks/llamaindex-react
2. LlamaIndex Mem0: https://developers.llamaindex.ai/python/examples/memory/mem0memory/
"""
import os
import asyncio
from dotenv import load_dotenv
from llama_index.core.tools import FunctionTool
from llama_index.memory.mem0 import Mem0Memory
from llama_index.llms.deepseek import DeepSeek
from llama_index.core.agent.workflow import FunctionAgent


load_dotenv(override=True)
os.environ["DEEPSEEK_API_KEY"] = os.environ["OPENAI_API_KEY"]

mem_config = {
    "llm": {
        "provider": "deepseek",
        "config": {
            "model": os.environ["MODEL_ID"]
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "bge-m3",
        }
    },
    "vector_store": {
        "config": {
            "embedding_model_dims": 1024
        }
    }
}
mem_context = {"user_id": "david"}

def call_fn(name: str):
    """Call the provided name.
    Args:
        name: str (Name of the person)
    """
    return f"Calling... {name}"

def email_fn(name: str):
    """Email the provided name.
    Args:
        name: str (Name of the person)
    """
    return f"Emailing... {name}"

def order_food(name: str, dish: str):
    """Order food for the provided name.
    Args:
        name: str (Name of the person)
        dish: str (Name of the dish)
    """
    return f"Ordering {dish} for {name}"


call_tool = FunctionTool.from_defaults(fn=call_fn)
email_tool = FunctionTool.from_defaults(fn=email_fn)
order_food_tool = FunctionTool.from_defaults(fn=order_food)


async def main(with_mem=True):
    # use deepseek as llm
    llm = DeepSeek(model=os.environ["MODEL_ID"], api_key=os.environ["OPENAI_API_KEY"], is_function_calling_model=True)

    mem_from_config = Mem0Memory.from_config(
        context=mem_context,
        config=mem_config,
        search_msg_limit=4
    )
    agent = FunctionAgent(
        tools=[call_tool, email_tool, order_food_tool],
        llm=llm,
        verbose=True,
    )

    while True:
        try:
            query = input("\033[36mChat >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        if with_mem:
            # with memory
            response = await agent.run(query, memory=mem_from_config)
        else:
            # without memory
            response = await agent.run(query)
        print(str(response))


if __name__ == "__main__":
    # asyncio.run(main(with_mem=False))
    asyncio.run(main(with_mem=True))