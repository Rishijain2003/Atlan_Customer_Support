import logging
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from rag import RAGSubgraph
from state import State
from prompt import ticket_structure, classification_prompt
from schema import Ticket, TicketClassification

# ----------------
# Logging setup
# ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
import os
# ----------------
# Query Node
# ----------------
# def query_input(state: State):
#     question = state.get("question", "")
    
#     if not question.strip():
#         return {"error": "No question provided"}
    
#     load_dotenv()
#     os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    
#     model = "gpt-4o-mini"
#     llm = ChatOpenAI(temperature=0.7, model_name=model)

#     formatted_prompt = ticket_structure.format(question=question)
#     logger.info(f"Formatted ticket prompt: {formatted_prompt}")
#     structured_llm1 = llm.with_structured_output(Ticket)
#     structured_ticket = structured_llm1.invoke(formatted_prompt)
#     logger.info(f"Extracted ticket: {structured_ticket}")

#     # 2️⃣ Classify ticket
#     ticket_classification = classification_prompt.format(
#         id=structured_ticket.id,
#         subject=structured_ticket.subject,
#         body=structured_ticket.body,
#     )
#     logger.info(f"Formatted classification prompt: {ticket_classification}")
#     structured_llm2 = llm.with_structured_output(TicketClassification)
#     result = structured_llm2.invoke(ticket_classification)

#     # Log results
#     logger.info(f"Structured ticket: {structured_ticket}")
#     logger.info(f"Ticket classification: {result}")

#     logger.info("*****************************************************************")
#     logger.info(f"Question: {question}")
#     logger.info(f"Ticket ID: {structured_ticket.id}")
#     logger.info(f"Subject: {structured_ticket.subject}")
#     logger.info(f"Body: {structured_ticket.body}")
#     logger.info(f"Topic Tag: {result.topic_tag}")
#     logger.info(f"Sentiment: {result.sentiment}")
#     logger.info(f"Priority: {result.priority}")
#     logger.info("*****************************************************************")
    
#     # Return full state for next node
#     return {
#         "question": question,
#         "id": structured_ticket.id,
#         "subject": structured_ticket.subject,
#         "body": structured_ticket.body,
#         "topic_tag": result.topic_tag,
#         "sentiment": result.sentiment,
#         "priority": result.priority,
#     }
def extract_ticket(state: State):
    """Extract a structured ticket (id, subject, body) from the question."""
    question = state.get("question", "")
    if not question.strip():
        return {"error": "No question provided"}
    
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    
    model = "gpt-4o-mini"
    llm = ChatOpenAI(temperature=0.7, model_name=model)

    formatted_prompt = ticket_structure.format(question=question)
    logger.info(f"Formatted ticket prompt: {formatted_prompt}")
    
    structured_llm = llm.with_structured_output(Ticket)
    structured_ticket = structured_llm.invoke(formatted_prompt)
    
    logger.info(f"Extracted ticket: {structured_ticket}")
    
    return {
        "question": question,
        "id": structured_ticket.id,
        "subject": structured_ticket.subject,
        "body": structured_ticket.body,
    }

def classify_ticket(state: State):
    """Classify a structured ticket into topic, sentiment, and priority."""
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')

    model = "gpt-4o-mini"
    llm = ChatOpenAI(temperature=0.7, model_name=model)

    ticket_classification = classification_prompt.format(
        id=state["id"],
        subject=state["subject"],
        body=state["body"],
    )
    logger.info(f"Formatted classification prompt: {ticket_classification}")
    
    structured_llm = llm.with_structured_output(TicketClassification)
    result = structured_llm.invoke(ticket_classification)
    
    logger.info(f"Ticket classification: {result}")
    
    return {
        **state,  # keep previous state (id, subject, body, question)
        "topic_tag": result.topic_tag,
        "sentiment": result.sentiment,
        "priority": result.priority,
    }

# ----------------
# Router Node
# ----------------
def router(state: State):
    q = state["topic_tag"]
    if q in ["How-to", "Product", "Connector"]:
        return "developer"
    elif q in ["API/SDK"]:
        return "documentation"
    else:
        return "last_node"

# def last_node(state:State):
#     logger.info("No suitable subgraph found for the given topic tag.")
#     result="This ticket has been classified as a 'Connector' issue and routed to the appropriate team."
#     sources=[]
#     return {"answer": result,"sources": sources}
from schema import AnswerWithSources  # import your Pydantic model

def last_node(state: State):
    logger.info("No suitable subgraph found for the given topic tag.")
    result = AnswerWithSources(
        answer="This ticket has been classified but no RAG lookup was needed.",
        sources=[]
    )
    return {
        
        "answer": result,
        "sources": []
    }



# ----------------
# Build Subgraphs
# ----------------
# dev_rag = RAGSubgraph("data/vector_store/developer_db").build()
# doc_rag = RAGSubgraph("data/vector_store/document_db").build()


# ----------------
# Parent Graph
# ----------------
# parent = StateGraph(State)

# parent.add_node("query_input", query_input)
# parent.add_node("router", router)
# parent.add_node("developer", dev_rag)
# parent.add_node("documentation", doc_rag)

# # Define execution flow
# parent.add_edge(START, "query_input")
# parent.add_edge("query_input", "router")

# parent.add_conditional_edges(
#     "router",
#     router,
#     {
#         "developer": "developer",
#         "documentation": "documentation",
#     }
# )

# # Subgraph outputs merge into parent state
# parent.add_edge("developer", END)
# parent.add_edge("documentation", END)

# Compile parent graph
# parent_graph = parent.compile()
def build_graph():
    parent = StateGraph(State)

    dev_rag = RAGSubgraph("data/vector_store/temp_db").build()
    doc_rag = RAGSubgraph("data/vector_store/temp_db").build()

    parent.add_node("extract_ticket", extract_ticket)
    parent.add_node("classify_ticket", classify_ticket)

    parent.add_node("developer", dev_rag)
    parent.add_node("documentation", doc_rag)
    parent.add_node("last_node", last_node)

    parent.add_edge(START, "extract_ticket")
    parent.add_edge("extract_ticket", "classify_ticket")

    # ✅ Router attached to classify_ticket
    parent.add_conditional_edges(
        "classify_ticket",
        router,
        {
            "developer": "developer",
            "documentation": "documentation",
            "last_node": "last_node",
        }
    )

    parent.add_edge("developer", END)
    parent.add_edge("documentation", END)
    parent.add_edge("last_node", END)

    return parent.compile()


# Main Function for Streamlit
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