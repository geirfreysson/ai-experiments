# /// script
# requires-python = ">=3.12.1"
# dependencies = [
#     "llama-index",
#     "llama-index-llms-openai",
# ]
# ///
# NOTE: This version is for Jupyter notebooks only!
# For standalone Python scripts, use two_tool_agent_llamaindex_script.py
import asyncio
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

def sum_numbers(numbers: list[float]) -> float:
    """
    Calculate the sum of a list of numbers.

    Args:
        numbers: A list of numbers to sum
    """
    return sum(numbers)

def divide_sum(total: float, length: int) -> float:
    """
    Divide a sum by a length to get the average.

    Args:
        total: The sum/total to divide
        length: The number to divide by (typically the count of numbers)
    """
    return total / length

# Create FunctionTools from the functions
sum_tool = FunctionTool.from_defaults(fn=sum_numbers)
divide_tool = FunctionTool.from_defaults(fn=divide_sum)

# Create LLM and agent
llm = OpenAI(model="gpt-4o-mini")
agent = ReActAgent(tools=[sum_tool, divide_tool], llm=llm, verbose=True)

# Create a context to store the conversation history/session state
#ctx = Context(agent)

# Run the agent and show intermediate steps
from llama_index.core.agent.workflow import AgentStream

handler = agent.run("What is the average of 10, 20, 30, 40, and 50?")
async for ev in handler.stream_events():
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)
response = await handler
print(f"\n\nFinal response: {response}")
