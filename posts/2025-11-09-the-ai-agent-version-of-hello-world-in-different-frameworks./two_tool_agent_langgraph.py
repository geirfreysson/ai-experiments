# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "langgraph",
#     "langchain-openai",
# ]
# ///
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
def sum_numbers(numbers: list[float]) -> float:
    """
    Calculate the sum of a list of numbers.

    Args:
        numbers: A list of numbers to sum
    """
    return sum(numbers)

@tool
def divide_sum(total: float, length: int) -> float:
    """
    Divide a sum by a length to get the average.

    Args:
        total: The sum/total to divide
        length: The number to divide by (typically the count of numbers)
    """
    return total / length

# Create LLM and agent
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, [sum_numbers, divide_sum])

# Run the agent with streaming to see intermediate steps
for chunk in agent.stream(
    {"messages": [("user", "What is the average of 10, 20, 30, 40, and 50?")]},
    stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
