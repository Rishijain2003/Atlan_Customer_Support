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

    def TicketClassifier(self, state: State):
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
            "topic_tags": result.topic_tags,
            "sentiment": result.sentiment,
            "priority": result.priority,
        }

 
    def router(self, state: State):
        """
        Determine the routing based on the topic_tag list.
        Prioritize 'developer' topics first, then 'documentation', otherwise 'last_node'.
        """
        topics = state.get("topic_tags", [])
        if not topics:  # fallback if empty
            return "last_node"

        # Define topic-to-route mapping
        route_mapping = {
            "How-to": "rag",
            "Product": "rag",
            "SSO": "rag",
            "API/SDK": "rag",
            "Best practices": "rag",     
        }

        # Check each topic in order
        for topic in topics:
            route = route_mapping.get(topic)
            if route:
                return route

        # Fallback
        return "AssignTeam"

   
    def AssignTeam(self, state: State):
        logger.info("No suitable subgraph found for the given topic tags.")
        topics = state.get("topic_tags", [])

        result = AnswerWithSources(
            answer=f"This ticket has been classified to {', '.join(topics)} and routed to the appropriate team",
            sources=[]
        )
        return {
            "answer": result,
            "sources": []
        }

    def build_graph(self):
        parent = StateGraph(State)


        rag = RAGAgent("atlandb").build()

        parent.add_node("TicketClassifier", self.TicketClassifier)
        parent.add_node("rag", rag)
        parent.add_node("AssignTeam", self.AssignTeam)

        parent.add_edge(START, "TicketClassifier")

        parent.add_conditional_edges(
            "TicketClassifier",
            self.router,
            {
                "rag": "rag",
                "AssignTeam": "AssignTeam",
            }
        )


        parent.add_edge("rag", END)
        parent.add_edge("AssignTeam", END)

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
