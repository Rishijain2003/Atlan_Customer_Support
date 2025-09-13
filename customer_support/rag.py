import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.vectorstores import Chroma
from state import State
from schema import AnswerWithSources
from prompt import retriever_content
from dotenv import load_dotenv
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    
 
class RAGSubgraph:
    
    def __init__(self, db_dir: str, model: str = "gpt-4o-mini"):
        self.db_dir = db_dir
        self.model = model
        self.embedder = OpenAIEmbeddings()
        
        self.llm = ChatOpenAI(temperature=0.7, model_name=self.model)

    def retrieve(self, state: State):
        vector_store = Chroma(
            persist_directory=self.db_dir,
            embedding_function=self.embedder
        )
        retrieved_docs = vector_store.similarity_search(state["question"])
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("*****************************************************************")
        logger.info(f"Retrieved {len(retrieved_docs)} documents for the query.")
        logger.info("*****************************************************************")
        
        return {"context": retrieved_docs}


    def generate(self, state: State):
        sources = []
        for doc in state["context"]:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                source_url = doc.metadata["source"]
                if source_url not in sources:
                    sources.append(source_url)
                    print(f"Source URL: {source_url}")

        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        formatted_prompt = retriever_content.format(
            context=docs_content,
            question=state["question"],
            source=sources
        )
        logger.info(f"Formatted generation prompt: {formatted_prompt}")
        structured_llm = self.llm.with_structured_output(AnswerWithSources)
        result = structured_llm.invoke(formatted_prompt)
        return {"answer": result, "sources": sources}

    def build(self):
        subgraph = StateGraph(State)
        subgraph.add_node("retrieve", self.retrieve)
        subgraph.add_node("generate", self.generate)

        subgraph.add_edge(START, "retrieve")
        subgraph.add_edge("retrieve", "generate")
        subgraph.add_edge("generate", END)

        return subgraph.compile()
