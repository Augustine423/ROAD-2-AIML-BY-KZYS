# SLIDE 74
# ============================================================
# AZURE AI VOICE API - SESSION CONFIGURATION
# ============================================================
{
  "type": "session.update",
  "session": {
    "modalities": [
      "text",
      "audio"
    ],

    "voice": {
      "type": "openai",
      "name": "alloy",
      "input_audio_noise_reduction": {
        "type": "azure_deep_noise_suppression"
      },
      "input_audio_echo_cancellation": {
        "type": "server_echo_cancellation"
      }
    },

    "instructions": "You are a helpful assistant. Be concise and friendly.",

    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "input_audio_sampling_rate": 24000,

    "turn_detection": {
      "type": "azure_semantic_vad",
      "threshold": 0.5,
      "prefix_padding_ms": 300,
      "silence_duration_ms": 500
    },

    "temperature": 0.8,
    "max_response_output_tokens": "inf"
  }
}



# SLIDE 74
# ============================================================
# AZURE AI VOICE API - ENTRA ID AUTHENTICATION
# Connects to the Azure AI Voice API using Microsoft Entra ID credentials instead of an API key.
# ============================================================

import asyncio

from azure.identity import DefaultAzureCredential  # DefaultAzureCredential() automatically uses the currently authenticated Azure identity.
from azure.ai.voicelive import connect


async def main():

    async with connect(
        endpoint="your-endpoint",  # Replace: your-endpoint with your Azure AI Voice endpoint
        credential=DefaultAzureCredential(),
        model="gpt-4o"
    ) as connection:

        # Your async code here
        pass


asyncio.run(main())



# SLIDE 74
# ============================================================
# AZURE AI VOICE API - API KEY AUTHENTICATION
# Connects to the Azure AI Voice API using an endpoint and API key credential.
# ============================================================

import asyncio

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive import connect


async def main():

    async with connect(
        endpoint="your-endpoint",   # Replace: your-endpoint with your Azure AI Voice endpoint
        credential=AzureKeyCredential("your-api-key"),    # Replace: your-api-key with your Azure AI resource key
        model="gpt-4o"
    ) as connection:

        # Your async code here
        pass


asyncio.run(main())



# SLIDE 74
# ============================================================
# CREATE AN AI VOICE AGENT
# Creates an Azure AI Foundry agent configured for voice interactions using Voice Live settings.
# ============================================================

import os
import json

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv()

# CONNECT TO THE AI FOUNDRY PROJECT
project_client = AIProjectClient(
    endpoint="PROJECT_ENDPOINT",
    credential=DefaultAzureCredential(),
)

# DEFINE VOICE LIVE CONFIGURATION
voice_live_config = {
    "session": {
        "voice": {
            "name": "en-US-Ava:DragonHDLatestNeural",
            "type": "azure-standard",
            "temperature": 0.8
        },
        "input_audio_transcription": {
            "model": "azure-speech"
        },
        "turn_detection": {
            "type": "azure_semantic_vad",
            "end_of_utterance_detection": {
                "model": "semantic_detection_v1_multilingual"
            }
        },
        "input_audio_noise_reduction": {
            "type": "azure_deep_noise_suppression"
        },
        "input_audio_echo_cancellation": {
            "type": "server_echo_cancellation"
        }
    }
}

# CREATE THE VOICE AGENT
agent = project_client.agents.create_version(
    agent_name="AGENT_NAME",
    definition=PromptAgentDefinition(
        model="MODEL_DEPLOYMENT_NAME",
        instructions="You are a helpful assistant."
    ),
    metadata=chunk_config(
        json.dumps(voice_live_config)
    )
)

# DISPLAY AGENT DETAILS
print(
    f"Agent created: "
    f"{agent.name} (version {agent.version})"
)