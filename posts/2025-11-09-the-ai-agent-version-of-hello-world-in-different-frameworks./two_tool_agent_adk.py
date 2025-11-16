# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-adk",
#     "google-genai",
# ]
# ///
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

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

# Create the agent with tools
agent = Agent(
    name="average_calculator",
    model="gemini-2.0-flash-exp",
    description="Agent that calculates averages using sum and divide operations.",
    instruction="You are a helpful agent that can calculate averages by first summing numbers and then dividing by the count.",
    tools=[sum_numbers, divide_sum]
)

# Create session service and runner
async def main():
    session_service = InMemorySessionService()

    # Create a session
    session = await session_service.create_session(
        state={},
        app_name="average_calculator_app",
        user_id="user"
    )

    runner = Runner(
        app_name="average_calculator_app",
        agent=agent,
        session_service=session_service
    )

    # Run the agent
    print("Running agent...\n")

    # Prepare the user's message in ADK format
    query = "What is the average of 10, 20, 30, 40, and 50?"
    content = types.Content(role='user', parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id="user",
        session_id=session.session_id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            print(f"{event.author}: {event.content.parts[0].text}")

asyncio.run(main())
