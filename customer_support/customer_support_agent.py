import logging
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from rag_builder import RAGAgent
from state import State
from prompt import classifier_prompt
from schema import AnswerWithSources, TicketClassificationModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        load_dotenv()
        os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')

        self.model_name = model
        self.temperature = temperature
        self.llm = ChatOpenAI(temperature=temperature, model_name=model)

    def classify_ticket(self, state: State):
        """Classify a structured ticket into topic, sentiment, and priority."""
        question = state.get("question", "")
        if not question.strip():
            return {"error": "No question provided"}

        ticket_classification = classifier_prompt.format(question=question)
        logger.info(f"Formatted classification prompt: {ticket_classification}")

        structured_llm = self.llm.with_structured_output(TicketClassificationModel)
        result = structured_llm.invoke(ticket_classification)

        logger.info(f"Ticket classification: {result}")

        return {
            "subject": result.subject,
            "body": result.body,
            "topic_tag": result.topic_tag,
            "sentiment": result.sentiment,
            "priority": result.priority,
        }

    def router(self, state: State):
        q = state["topic_tag"]
        if q in ["How-to", "Product", "Connector"]:
            return "documentation"
        elif q in ["API/SDK"]:
            return "developer"
        else:
            return "last_node"

    def last_node(self, state: State):
        logger.info("No suitable subgraph found for the given topic tag.")
        topic = state.get("topic_tag", "")

        result = AnswerWithSources(
            answer=f"This ticket has been classified to {topic} and routed to the appropriate team",
            sources=[]
        )
        return {
            "answer": result,
            "sources": []
        }

    def build_graph(self):
        parent = StateGraph(State)

        dev_rag = RAGAgent("developmentdb").build()
        doc_rag = RAGAgent("documentdb").build()

        parent.add_node("classify_ticket", self.classify_ticket)
        parent.add_node("developer", dev_rag)
        parent.add_node("documentation", doc_rag)
        parent.add_node("last_node", self.last_node)

        parent.add_edge(START, "classify_ticket")

        parent.add_conditional_edges(
            "classify_ticket",
            self.router,
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

    def run_graph(self, question: str):
        """
        Main function to be called externally.
        
        Args:
            question (str): The user's query
        
        Returns:
            dict: Complete state with all results
        """
        try:
            graph = self.build_graph()
            result = graph.invoke({"question": question})
            return result
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            return {"error": str(e)}
