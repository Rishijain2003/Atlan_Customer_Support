from pydantic import BaseModel, Field
from typing import List, Literal
class Page(BaseModel):
    url: str
    title: str
    content: str

class AnswerWithSources(BaseModel):
    """An answer to the question, with sources."""
    answer: str
    sources: List[str]

class Ticket(BaseModel):
    id: str = Field(..., description="Unique ticket id starting with TICKET- and a number")
    subject: str = Field(..., description="Short subject line summarizing the issue")
    body: str = Field(..., description="Full user query body as provided")

    
class TicketClassificationModel(BaseModel):  
    """Classification fields only - no ticket content"""
    subject: str = Field(..., description="Short subject line summarizing the issue")
    body: str = Field(..., description="Full user query body as provided")
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