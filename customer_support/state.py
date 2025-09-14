from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from schema import AnswerWithSources

class State(TypedDict):
    question: str
    context: List[Document]
    answer: AnswerWithSources
    id: str               
    subject: str          
    body: str             
    topic_tags: List[str]        # One of the controlled vocabulary
    sentiment: str        # Frustrated | Curious | Angry | Neutral
    priority: str         # P0 | P1 | P2
