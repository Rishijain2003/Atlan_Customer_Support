import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal, List
from customer_support.prompt import classification_prompt

# Load API key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("Openai_api_key")

# Pydantic Model supporting multiple topic tags
class TicketClassification(BaseModel):
    """Classification fields only - no ticket content"""
    topic_tags: List[Literal[
        "How-to",
        "Product",
        "Connector",
        "Lineage",
        "API/SDK",
        "SSO",
        "Glossary",
        "Best practices",
        "Sensitive data"
    ]] = Field(..., description="One or more topic tags for the ticket")
    
    sentiment: Literal["Frustrated", "Curious", "Angry", "Neutral"]
    priority: Literal["P0", "P1", "P2"]

# Initialize LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
structured_llm = llm.with_structured_output(TicketClassification)

# Classification function
def classify_tickets(input_file, output_file):

    # Load tickets from JSON
    with open(input_file, "r", encoding="utf-8") as f:
        tickets = json.load(f)

    results = []

    for ticket in tickets:
        ticket_classification_prompt = classification_prompt.format(
            id=ticket["id"],
            subject=ticket["subject"],
            body=ticket["body"],
        )

        print(f"Classifying Ticket ID: {ticket['id']}")

        # Invoke LLM with structured output
        result = structured_llm.invoke(ticket_classification_prompt)
        result_dict = result.model_dump()

        # Ensure topic_tags is always a list
        if isinstance(result_dict["topic_tags"], str):
            result_dict["topic_tags"] = [result_dict["topic_tags"]]


        print(f"Structured Response: {result_dict}")

        results.append({
            "id": ticket["id"],
            "subject": ticket["subject"],
            "body": ticket["body"],
            **result_dict
        })

 
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Classified tickets saved to {output_file}")

# Run the classification
if __name__ == "__main__":
    classify_tickets("classifier/sample_tickets.json", "classifier/sample_ticket_c.json")
