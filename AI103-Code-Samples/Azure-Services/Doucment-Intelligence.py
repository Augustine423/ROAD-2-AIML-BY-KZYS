# SLIDE 72
# ============================================================
# AZURE AI DOCUMENT INTELLIGENCE - ANALYZE A DOCUMENT
# Analyzes a document using a custom Document Intelligence model and returns the extracted results.
# ============================================================

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# CONNECT TO DOCUMENT INTELLIGENCE
document_analysis_client = DocumentAnalysisClient(
    endpoint="YOUR_DOC_INTELLIGENCE_ENDPOINT",
    credential=AzureKeyCredential(
        "YOUR_DOC_INTELLIGENCE_KEY"
    )
)

# ANALYZE THE DOCUMENT
task = (
    document_analysis_client.begin_analyze_document_from_url(
        model_id = "YOUR_CUSTOM_BUILT_MODEL_ID",
        form_url = "YOUR_DOCUMENT"
    )
)

# Wait for analysis to complete
result = task.result()

# RESULT
print(result)