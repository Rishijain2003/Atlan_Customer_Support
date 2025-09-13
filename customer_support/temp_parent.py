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
# Query Node
# ----------------
def query_input(state: State):
    """Prompt user for a question and return structured ticket + classification."""
    question = input("\nPlease enter your support query (or type 'exit' to quit): ")
    if question.strip().lower() == "exit":
        return None  # signal to stop
    
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
# Build Subgraph
# ----------------
temp_rag = RAGSubgraph("data/vector_store/temp_db").build()

# ----------------
# Parent Graph
# ----------------
parent = StateGraph(State)

parent.add_node("query_input", query_input)
parent.add_node("temp_rag", temp_rag)

# Define execution flow: query_input -> temp_rag -> END
parent.add_edge(START, "query_input")
parent.add_edge("query_input", "temp_rag")
parent.add_edge("temp_rag", END)

parent_graph = parent.compile()

# ----------------
# Interactive Loop
# ----------------
print("=== Interactive Support Assistant ===")
while True:
    try:
        # Use .invoke() instead of .execute()
        state = parent_graph.invoke({})  # empty dict as starting state
        
        # Check if user wants to exit
        if state.get("should_exit"):
            print("Exiting assistant. Goodbye!")
            break

        # Check for errors
        if "error" in state:
            print(f"\nError occurred: {state['error']}")
            continue

        # Print summarized response from temp_rag
        if "answer" in state:
            print("\n--- Answer ---")
            print(state["answer"].answer)
            print("\nSources:", state["answer"].sources)
        else:
            print("\nNo answer returned from RAG subgraph.")
    
    except Exception as e:
        logger.error(f"Graph execution error: {e}")
        print(f"An error occurred: {e}")
        continue
