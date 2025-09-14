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
    topic_tags: List[str]        
    sentiment: str        
    priority: str        
