# SLIDE 17
# ============================================================
# CONNECT TO AN AZURE AI FOUNDRY PROJECT
# Creates a client connection to an Azure AI Foundry project. Replace <resource-name> and <project-name> with your values.
# ============================================================

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(  # project_client can now be used to interact with your Azure AI Foundry project resources.
    credential=DefaultAzureCredential(),
    endpoint="https://<resource-name>.services.ai.azure.com/api/projects/<project-name>"
)



# SLIDE 17
# ============================================================
# CONNECT TO AN AZURE OPENAI ENDPOINT (ENTRA ID AUTHENTICATION)
# Uses Microsoft Entra ID instead of an API key to authenticate with an Azure OpenAI resource.
# ============================================================

from azure.identity import (DefaultAzureCredential, get_bearer_token_provider)
from openai import OpenAI

token_provider = get_bearer_token_provider(   # Create a token provider using your Azure credentials
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

openai_client = OpenAI(      # Create an Azure OpenAI client
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",  # Replace <resource-name> with your Azure OpenAI resource name.
    api_key=token_provider,
)



# SLIDE 17
# ============================================================
# CONNECT TO AN AZURE OPENAI ENDPOINT (API KEY)
# Uses an Azure OpenAI API key stored in an environment variable to authenticate requests.
# ============================================================

import os
from openai import OpenAI

# Create an Azure OpenAI client
openai_client = OpenAI(
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",    # Replace <resource-name> with your Azure OpenAI resource name.
    api_key=os.getenv("AZURE_OPENAI_API_KEY")     # Ensure the AZURE_OPENAI_API_KEY environment variable is set.
)



# SLIDE 17
# ============================================================
# CONNECT TO A SPECIFIC AZURE OPENAI API VERSION (API KEY)
# Uses the AzureOpenAI client to connect to an Azure OpenAI resource and target a specific API version.
# ============================================================

import os
from openai import AzureOpenAI

# Create an Azure OpenAI client
openai_client = AzureOpenAI(
    azure_endpoint="https://<resource-name>.openai.azure.com/",     # Replace <resource-name> with your Azure OpenAI resource name.
    api_key=os.getenv("AZURE_OPENAI_KEY"),    # Ensure the AZURE_OPENAI_KEY environment variable is set.
    api_version="2024-10-21"     # Update api_version as needed for your implementation.
)



# SLIDE 18
# ============================================================
# GENERATE RESPONSES USING THE RESPONSES API
# ============================================================

import time

# Create a Vector Store - Used by the File Search tool to search uploaded documents.
vector_store = client.vector_stores.create(
    name="policy-docs"
)

# Upload a File to the Vector Store
client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id,
    file=open("expenses_policy.pdf", "rb")
)

# Custom Function - Example function that can be called by the model.
def get_time():
    return (
        f"The time is "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
    )

# Generate a Response
response = openai_client.responses.create(
    model="gpt-4.1",  # Model deployment name
    instructions=("You are a helpful AI assistant that answers questions clearly."),
    input="What is Microsoft Foundry?",
    temperature=0.8,
    max_output_tokens=200,
    previous_response_id=last_response_id,     # Continue a previous conversation
    tools=[       # Available tools
        {
            "type": "code_interpreter",
            "container": {"type": "auto"}
        },
        {
            "type": "web_search"
        },
        {
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        },
        {
            "type": "function",
            "name": "get_time",
            "description": "Get the current time."
        }
    ],
    stream=True       # Stream output as it is generated
)

# Save Response ID for Conversation Context
last_response_id = response.id

# Display Response Details
print(f"Response: {response.output_text}")
print(f"Response ID: {response.id}")
print(f"Tokens Used: {response.usage.total_tokens}")
print(f"Status: {response.status}")

# Display Streaming Output
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="")

    elif event.type == "response.completed":
        response_id = event.response.id



# SLIDE 18
# ============================================================
# RETRIEVE A PREVIOUS RESPONSE
# Retrieves a previously generated response using its unique response ID for reviewing, auditing, or continuing conversations.
# ============================================================

try:
    response_id = "resp_67cb61fa3a448190bcf2c42d96f0d1a8"     # Response ID to retrieve

    previous_response = openai_client.responses.retrieve(      # Retrieve the previous response
        response_id
    )

    # Display the response text
    print(f"Previous Response: {previous_response.output_text}")

except Exception as ex:
    print(f"Error: {ex}")



# SLIDE 18
# ============================================================
# ASYNC RESPONSES API
# Uses the asynchronous OpenAI client to generate responses without blocking your application while waiting for results.
# ============================================================

import asyncio
from openai import AsyncOpenAI

# Create an Azure OpenAI client
client = AsyncOpenAI(
    base_url="https://<resource-name>.openai.azure.com/openai/v1/",
    api_key=token_provider
)

# Generate an Asynchronous Response
async def main():
    response = await client.responses.create(
        model="gpt-4.1",
        input="Explain quantum computing briefly."
    )

    print(response.output_text)

# Run the Asynchronous Function
asyncio.run(main())



# SLIDE 18
# ============================================================
# CHAT COMPLETIONS API
# Sends messages to a chat model and receives a response. Conversation history is maintained by passing previous messages with each request.
# ============================================================

# Initialize the conversation
conversation_messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant that answers questions and provides information."
    },
    {
        "role": "user",
        "content": "When was Microsoft founded?"
    }
]

# First Chat Completion

completion = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=conversation_messages
)

assistant_text = completion.choices[0].message.content

print("Assistant:", assistant_text)

# Add the assistant's reply to the conversation
conversation_messages.append(
    {
        "role": "assistant",
        "content": assistant_text
    }
)

# Add Another User Message
conversation_messages.append(
    {
        "role": "user",
        "content": "Who founded it?"
    }
)

# Second Chat Completion
completion = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=conversation_messages
)

assistant_text = completion.choices[0].message.content

print("Assistant:", assistant_text)

# Continue appending messages and sending the full conversation history to maintain context.
#The entire array conversation_messages would look like this:
completion = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant that answers questions and provides information."},
        {"role": "user", "content": "When was Microsoft founded?"},
        {"role": "assistant", "content": "<Agent Output>"},
        {"role": "user", "content": "Who founded it?"}
    ]
)



# SLIDE 20
# ============================================================
# AI FOUNDRY AGENT (YAML)
# Defines an AI agent in VS Code using YAML.
# ============================================================

# yaml-language-server: $schema=https://aka.ms/ai-foundry-vsc/agent/1.0.0

# version: 1.0.0
# name: healthcare-assistant
# description: Assists healthcare staff with patient appointment scheduling and information retrieval.
# id: "agent-abc123xyz"
#     metadata:
#         authors: - developer-name
#         tags: - healthcare - customer-service - scheduling
#         model:
#             id: "gpt-4.1"
#             options:
#                 temperature: 0.5
#                 top_p: 1

# instructions: |
#   You're a healthcare assistant helping staff schedule patient appointments and retrieve information.

#   Your responsibilities:
#   - Help staff find available appointment slots.
#   - Answer questions about patient scheduling policies.
#   - Provide information about different appointment types.
#   - Assist with rescheduling and cancellations.

#   Important guidelines:
#   - Never access or share patient medical information.
#   - Always verify appointment details before confirming.
#   - Be professional but friendly in all interactions.
#   - If unsure about policies, advise staff to check with management.

# tools:
#   - type: code_interpreter
#   - type: bing_grounding
#     bing_grounding:
#       connection_id: "your-connection-id"
#   - type: file_search
#     file_search:
#       vector_store_ids:
#         - "vectorstore-123"



# SLIDE 31
# ============================================================
# CREATE AN AI FOUNDRY AGENT WITH CUSTOM TOOLS
# ============================================================

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (PromptAgentDefinition, MCPTool, FunctionTool, Tool)

# Connect to the AI Foundry Project
project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)

# Create a Custom Function Tool - Allows the agent to retrieve recent snowfall totals.
function_tool = FunctionTool(
    name="recent_snowfall",
    description="Get recent snowfall totals for a given location.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": (
                    "The city name to check snowfall for."
                )
            }
        },
        "required": ["location"],
        "additionalProperties": False
    },
    strict=True
)

# Connect to a Knowledge Base via MCP - Allows the agent to access external information sources.
knowledge_tool = MCPTool(
    server_label="product-docs",
    server_url=(
        f"{search_endpoint}/knowledgebases/"
        "product-documentation/mcp"
    ),
    require_approval="always"
)

# Create the Agent
agent = project_client.agents.create_version(
    name="snowfall-agent",
    definition=PromptAgentDefinition(
        model="gpt-4.1",
        instructions=(
            "You are a weather assistant tracking snowfall. "
            "Use the provided functions to answer questions."
        ),
        tools=[
            function_tool,
            knowledge_tool
        ]
    )
)