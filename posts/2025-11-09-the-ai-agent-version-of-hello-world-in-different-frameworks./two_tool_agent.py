# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "smolagents",
#     "litellm",
# ]
# ///
from smolagents import ToolCallingAgent, LiteLLMModel, tool

@tool
def sum_numbers(numbers: list[float]) -> float:
    """
    PLEASE Calculate the sum of a list of numbers.

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

model = LiteLLMModel(model_id="gpt-4o-mini")
agent = ToolCallingAgent(tools=[sum_numbers, divide_sum], model=model)
agent.run("What is the average of 10, 20, 30, 40, and 50?")

