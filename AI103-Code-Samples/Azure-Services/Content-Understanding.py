# SLIDE 71
# ============================================================
# AZURE AI CONTENT UNDERSTANDING - CREATE AN ANALYZER
# Creates a custom Content Understanding analyzer for extracting information from business cards.
# ============================================================

from azure.ai.contentunderstanding import (
    ContentUnderstandingClient
)

# DEFINE THE ANALYZER

analyzer_name = "business_card_analyser"

analyzer_definition = {
    "description": "Simple business card",
    "baseAnalyzerId": "prebuilt-document",

    "config": {
        "returnDetails": True
    },

    "fieldSchema": {    # This analyzer extracts: ContactName and EmailAddress from documents such as business cards.
        "fields": {
            "ContactName": {
                "type": "string",
                "method": "extract",
                "description": "Name on business card"
            },
            "EmailAddress": {
                "type": "string",
                "method": "extract",
                "description": "Email address on business card"
            }
        }
    },

    "models": {
        "completion": "gpt-4.1",
        "embedding": "text-embedding-3-large"
    }
}

# CREATE THE ANALYZER
poller = client.begin_create_analyzer(
    analyzer_name,
    body=analyzer_definition
)

# Wait for completion
result = poller.result()

# Display analyzer details
print(
    f"Analyzer created: {result.analyzer_id}"
)



# SLIDE 71
# ============================================================
# AZURE AI CONTENT UNDERSTANDING - ANALYZE CONTENT
# Analyzes content (such as an image) using a Content Understanding analyzer and returns structured results.
# ============================================================

import json
import sys

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult
)

# ANALYZE AN IMAGE FILE
with open("my_image.png", "rb") as f:

    file_bytes = f.read()

try:

    poller = client.begin_analyze(
        analyzer_id="ANALYZER_ID",  # Replace ANALYZER_ID with the ID of your Content Understanding analyzer.
        inputs=[
            AnalysisInput(
                data=file_bytes
            )
        ]
    )

    # Get analysis results
    result: AnalysisResult = poller.result()

    # Display results
    result_str = json.dumps(
        result.as_dict(),
        indent=2
    )

    print(result_str)

except Exception as ex:

    print(f"[Unexpected Error]: {ex}")
    sys.exit(1)