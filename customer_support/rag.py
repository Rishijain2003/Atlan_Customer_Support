import os
import glob
from dotenv import load_dotenv
# import gradio as gr
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma


import bs4
from langchain_community.document_loaders import WebBaseLoader

import os
from typing_extensions import List, TypedDict
from langchain import hub
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain_community.vectorstores import Chroma
from state import State
from schema import AnswerWithSources
from prompt import retriever_content
from dotenv import load_dotenv
# load_dotenv()


# llm = ChatOpenAI(temperature=0.7, model_name=MODEL)

# db_name="vector_db"


# page_url = ["https://docs.atlan.com/faq/basic-platform-usage","https://docs.atlan.com/platform/references/security-monitoring","https://docs.atlan.com/"]

# loader = WebBaseLoader(web_paths=page_url)
# # loader = UnstructuredLoader(web_url=page_url)
# docs = []
# # async for doc in loader.alazy_load():
# #     docs.append(doc)
# docs = loader.load()
# # --- Split documents into chunks ---
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# chunks = text_splitter.split_documents(docs)
# embed=OpenAIEmbeddings()
# if os.path.exists(db_name):
#     Chroma(persist_directory=db_name, embedding_function=embed).delete_collection()

# vector_store = Chroma.from_documents(
#     documents=chunks,
#     embedding=embed,
#     persist_directory=db_name
# )


# def retrieve(state: State):
#     DB_DIR = "data/vector_store/developer_db"
#     vector_store = Chroma(persist_directory=DB_DIR, embedding_function=OpenAIEmbeddings())
#     retrieved_docs = vector_store.similarity_search(state["question"])
#     return {"context": retrieved_docs}

# def generate(state: State):
    
#     MODEL = "gpt-4o-mini"
#     llm = ChatOpenAI(temperature=0.7, model_name=MODEL)
#     sources = []
#     for doc in state["context"]:
#         if hasattr(doc, 'metadata') and 'source' in doc.metadata:
#             source_url = doc.metadata['source']
#             if source_url not in sources:  # Avoid duplicates
#                 sources.append(source_url)
#                 print(f"Source URL: {source_url}")
                
    
#     docs_content = "\n\n".join(doc.page_content for doc in state["context"])
#     formatted_prompt = retriever_content.format(
#         context=docs_content,
#         question=state["question"],
#         source=sources    
#     )
#     # messages = forprompt.invoke({"question": state["question"], "context": docs_content})
#     structured_llm = llm.with_structured_output(AnswerWithSources)
#     result = structured_llm.invoke(formatted_prompt)
    
#     # response = structured_llm.invoke(messages)
#     # return {"answer": response}
#     return {"answer": result}




# # Compile application and test
# graph_builder = StateGraph(State).add_sequence([retrieve, generate])
# graph_builder.add_edge(START, "retrieve")
# graph = graph_builder.compile()
# result = graph.invoke({"question": "what is the availabilty of atlan and Security Monitoring?"})

# print(f"Context: {result['context']}\n\n")
# print(f"Answer: {result['answer']}")


# def build_dev_subgraph():
#     subgraph = StateGraph(State)
#     subgraph.add_node("retrieve", retrieve)
#     subgraph.add_node("generate", generate)

#     subgraph.add_edge(START, "retrieve")
#     subgraph.add_edge("retrieve", "generate")
#     subgraph.add_edge("generate", END)

#     return subgraph.compile()
import logging

from langgraph.graph import StateGraph, START, END
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from schema import AnswerWithSources
from prompt import retriever_content
from state import State
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv
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
