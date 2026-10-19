# SLIDE 67
# ============================================================
# AZURE AI LANGUAGE - LANGUAGE DETECTION
# Detects the language of one or more text documents and returns the language, ISO code, and confidence score.
# ============================================================

# Example documents to analyze
documents = [
    "Hello World!",
    "Bonjour le monde!"
]

# Detect the language of each document
response = client.detect_language(
    documents=documents
)

# Display results
for doc in response:
    print(f"Document ID: {doc.id}")
    print(f"\tLanguage: {doc.primary_language.name}")
    print(f"\tISO Code: {doc.primary_language.iso6391_name}")
    print(
        f"\tConfidence Score: "
        f"{doc.primary_language.confidence_score}"
    )

# Example Output:

# Document ID: 0
#   Language: English
#   ISO Code: en
#   Confidence Score: 1.0

# Document ID: 1
#   Language: French
#   ISO Code: fr
#   Confidence Score: 1.0



# SLIDE 67
# ============================================================
# AZURE AI LANGUAGE - NAMED ENTITY RECOGNITION (NER)
# ============================================================

# Example documents to analyze
documents = [
    "Microsoft was founded on April 4, 1975 by Bill Gates and Paul Allen in Albuquerque, New Mexico.",
    "Satya Nadella became CEO of Microsoft on February 4, 2014."
]

# Extract named entities
response = client.recognize_entities(
    documents=documents
)

# Display the detected entities
for doc in response:
    print(f"Entities in Document {doc.id}:")

    for entity in doc.entities:
        print(
            f" - {entity.text} "
            f"({entity.category})"
        )

# Example Output:

# Entities in Document 0:
# - Microsoft (Organization)
# - April 4, 1975 (DateTime)
# - Bill Gates (Person)
# - Paul Allen (Person)
# - Albuquerque (Location)
# - New Mexico (Location)

# Entities in Document 1:
# - Satya Nadella (Person)
# - Microsoft (Organization)
# - February 4, 2014 (DateTime)



# SLIDE 67
# ============================================================
# AZURE AI LANGUAGE - PERSONALLY IDENTIFIABLE INFORMATION (PII)
# ============================================================

# Example documents to analyze
documents = [
    "John Smith works at Contoso Ltd. His email is john.smith@contoso.com and his phone number is 555-012-456.",
    "Patient Sarah Johnson, SSN 123-45-6789, was admitted on 03/15/2024."
]

# Detect PII entities
response = client.recognize_pii_entities(
    documents=documents,
    language="en"
)

# Display results
for doc in response:

    print(f"\nPII Entities in Document {doc.id}:")

    # Display detected PII entities
    for entity in doc.entities:
        print(
            f" - {entity.text}: "
            f"{entity.category} "
            f"(Confidence: {entity.confidence_score:.2f})"
        )

    # Display text with PII automatically redacted
    print("\nRedacted Text:")
    print(doc.redacted_text)

# Example Output:

# PII Entities in Document 0:
#  - John Smith: Person
#  - john.smith@contoso.com: Email
#  - 555-012-456: PhoneNumber
# Redacted Text: [PERSON] works at Contoso Ltd. His email is [EMAIL] and his phone number is [PHONENUMBER].

# PII Entities in Document 1:
#  - Sarah Johnson: Person
#  - 123-45-6789: USSocialSecurityNumber
# Redacted Text:  Patient [PERSON], SSN [USSOCIALSECURITYNUMBER], was admitted on 03/15/2024.