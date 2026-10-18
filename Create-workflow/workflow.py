import os
import json
import re
from dotenv import load_dotenv

# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def print_workflow_output(output_text):
    # Safe handling if output_text is None or empty
    if not output_text:
        print("No output text received.")
        return

    tickets = re.findall(r"(\{.*?\})(.*?)(?=\{|$)", output_text, re.DOTALL)

    if not tickets:
        print(output_text)
        return

    for ticket_number, match in enumerate(tickets, start=1):
        try:
            ticket_json, response_text = match
            ticket = json.loads(ticket_json)

            print("\n" + "=" * 80)
            print(f"Ticket {ticket_number}: {ticket.get('category', 'Unknown')} ({ticket.get('confidence', 0):.0%} confidence)")
            print("-" * 80)
            print(f"Issue: {ticket.get('customer_issue', 'N/A')}")
            print("\nResponse:")
            print(response_text.strip())
        except json.JSONDecodeError:
            print(f"Could not parse JSON for ticket {ticket_number}. Raw text:")
            print(match)
    print("=" * 80 + "\n")

def main():
    load_dotenv()
    endpoint = os.environ["PROJECT_ENDPOINT"]

    # Connect to the AI Project client
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        # Specify the workflow
        workflow = {
            "name": "ContosoPay-Customer-Support-Triage"
        } 

        # Create a conversation and run the workflow
        conversation = openai_client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        stream = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent_reference" : {"name" : workflow["name"], "type": "agent_reference"}},
            input="Start",
            stream=True,
        )

        # Process events from the workflow run
        for event in stream:
            if event.type == "response.completed":
                print("\nResponse completed:")
                response = openai_client.responses.retrieve(event.response.id)
                print_workflow_output(response.output_text)

        # Clean up resources (Must be inside the 'with' block where openai_client is active)
        openai_client.conversations.delete(conversation_id=conversation.id)
        print("\nConversation deleted")

if __name__ == "__main__":
    main()