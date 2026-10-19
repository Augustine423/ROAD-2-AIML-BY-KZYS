import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add references
from agent_framework import tool, Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field
from typing import Annotated

# Load environment variables at the very beginning
load_dotenv()


# 1. Define the tool function first (Best Practice: Define functions before using them)
@tool(approval_mode="never_require")
def submit_claim(
    to: Annotated[str, Field(description="Who to send the email to")],
    subject: Annotated[str, Field(description="The subject of the email.")],
    body: Annotated[str, Field(description="The text body of the email.")]
):
    """Submit an expense claim by printing/sending the details."""
    print("\nTo:", to)
    print("Subject:", subject)
    print(body, "\n")


# 2. Define the agent processing function
async def process_expenses_data(prompt, expenses_data):
    """Initialize the Foundry chat client, create the agent, and process the data."""
    
    # Create a foundry chat client
    client = FoundryChatClient(
        project_endpoint=os.getenv("PROJECT_ENDPOINT"),
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        credential=AzureCliCredential()
    )    

    # Initialize an agent with the tool and instructions using an async context manager
    async with Agent(
        client=client,
        name="ExpenseClaimAgent",
        instructions="""You are an AI assistant for expense claim submission.
        At the user's request, create an expense claim and use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim' and a body that contains itemized expenses with a total.
        Then confirm to the user that you've done so. Don't ask for any more information from the user, just use the data provided to create the email.""",
        tools=[submit_claim],
    ) as agent: 

        # Use the agent to process the expenses data 
        try:
            # Add the input prompt to a list of messages to be submitted
            prompt_messages = [f"{prompt}: {expenses_data}"]
            
            # Invoke the agent for the specified thread with the messages
            response = await agent.run(prompt_messages)
            
            # Display the response
            print(f"\n# Agent:\n{response}")
            
        except Exception as e:
            # Handle any execution errors gracefully
            print(f"An error occurred while running the agent: {e}")


# 3. Main entry point
async def main():
    # Clear the console for a clean output screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load the expenses data file safely using pathlib
    script_dir = Path(__file__).parent
    file_path = script_dir / 'data.txt'
    
    if not file_path.exists():
        print(f"Error: Could not find '{file_path}'. Please make sure 'data.txt' exists.")
        return

    with file_path.open('r', encoding='utf-8') as file:
        data = file.read() + "\n"

    # Ask for a prompt from the user
    user_prompt = input(f"Here is the expenses data in your file:\n\n{data}\n\nWhat would you like me to do with it?\n\n")
    
    if not user_prompt.strip():
        print("Prompt cannot be empty.")
        return

    # Run the async agent code process
    await process_expenses_data(user_prompt, data)


if __name__ == "__main__":
    asyncio.run(main())