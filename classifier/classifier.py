import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal
from prompt import classification_prompt

# ------------------------
# Load API key
# ------------------------
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("Openai_api_key")


# ------------------------
# Pydantic Model
# ------------------------
class TicketClassification(BaseModel):
    """Classification fields only - no ticket content"""
    topic_tag: Literal[
        "How-to",
        "Product",
        "Connector",
        "Lineage",
        "API/SDK",
        "SSO",
        "Glossary",
        "Best practices",
        "Sensitive data"
    ]
    sentiment: Literal["Frustrated", "Curious", "Angry", "Neutral"]
    priority: Literal["P0", "P1", "P2"]


llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
structured_llm = llm.with_structured_output(TicketClassification)


# ------------------------
# Classification function
# ------------------------
def classify_tickets(input_file, output_file):
    # Load tickets
    with open(input_file, "r", encoding="utf-8") as f:
        tickets = json.load(f)

    results = []
    structured_llm = llm.with_structured_output(TicketClassification)
    for ticket in tickets:
        ticket_classification = classification_prompt.format(
            id=ticket["id"],
            subject=ticket["subject"],
            body=ticket["body"],
        )
        print(f"Classifying Ticket ID: {ticket['id']}")
        
        result = structured_llm.invoke(ticket_classification)
        print("******************************************************************************")
        print(f"Structured Response: {result}")
        print("******************************************************************************")

        # since result is already parsed into Pydantic model, just use .dict()
        results.append({
            "id": ticket["id"],
            "subject": ticket["subject"],
            "body": ticket["body"],
            **result.dict()
        })

    # Save to output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Classified tickets saved to {output_file}")


# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    classify_tickets("sample_tickets.json", "sample_ticket_classified.json")
