import logging
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import os
from rag import RAGSubgraph
from state import State
from prompt import ticket_structure, classification_prompt
from schema import Ticket, TicketClassification
from dotenv import load_dotenv

# ----------------
# Logging setup
# ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------
# Query Processing Node (Modified - no input())
# ----------------
def process_query(state: State):
    """Process the question from state and return structured ticket + classification."""
    question = state.get("question", "")
    
    if not question.strip():
        return {"error": "No question provided"}
    
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    
    model = "gpt-4o-mini"
    llm = ChatOpenAI(temperature=0.7, model_name=model)

    # 1️⃣ Extract ticket details
    formatted_prompt = ticket_structure.format(question=question)
    logger.info(f"Formatted ticket prompt: {formatted_prompt}")
    structured_llm1 = llm.with_structured_output(Ticket)
    structured_ticket = structured_llm1.invoke(formatted_prompt)
    logger.info(f"Extracted ticket: {structured_ticket}")

    # 2️⃣ Classify ticket
    ticket_classification = classification_prompt.format(
        id=structured_ticket.id,
        subject=structured_ticket.subject,
        body=structured_ticket.body,
    )
    logger.info(f"Formatted classification prompt: {ticket_classification}")
    structured_llm2 = llm.with_structured_output(TicketClassification)
    result = structured_llm2.invoke(ticket_classification)

    # Log results
    logger.info(f"Structured ticket: {structured_ticket}")
    logger.info(f"Ticket classification: {result}")

    logger.info("*****************************************************************")
    logger.info(f"Question: {question}")
    logger.info(f"Ticket ID: {structured_ticket.id}")
    logger.info(f"Subject: {structured_ticket.subject}")
    logger.info(f"Body: {structured_ticket.body}")
    logger.info(f"Topic Tag: {result.topic_tag}")
    logger.info(f"Sentiment: {result.sentiment}")
    logger.info(f"Priority: {result.priority}")
    logger.info("*****************************************************************")
    
    # Return full state for next node
    return {
        "question": question,
        "id": structured_ticket.id,
        "subject": structured_ticket.subject,
        "body": structured_ticket.body,
        "topic_tag": result.topic_tag,
        "sentiment": result.sentiment,
        "priority": result.priority,
    }

# ----------------
# Build Graph
# ----------------
def build_graph():
    """Build and compile the complete graph."""
    # Build RAG subgraph
    temp_rag = RAGSubgraph("data/vector_store/temp_db").build()
    
    # Build parent graph
    parent = StateGraph(State)
    parent.add_node("process_query", process_query)
    parent.add_node("temp_rag", temp_rag)
    
    # Define execution flow
    parent.add_edge(START, "process_query")
    parent.add_edge("process_query", "temp_rag")
    parent.add_edge("temp_rag", END)
    
    return parent.compile()

# ----------------
# Main Function for Streamlit
# ----------------
def run_graph(question: str):
    """
    Main function to be called from Streamlit.
    
    Args:
        question (str): The user's query
        
    Returns:
        dict: Complete state with all results
    """
    try:
        # Build graph
        graph = build_graph()
        
        # Run graph with the question
        result = graph.invoke({"question": question})
        
        return result
    except Exception as e:
        logger.error(f"Graph execution error: {e}")
        return {"error": str(e)}