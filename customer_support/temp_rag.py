# app/rag_node1.py
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv



def create_rag_pipeline():
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    MODEL = "gpt-4o-mini"
    DB_DIR = "data/vector_store/temp_db"
    
    vectordb = Chroma(persist_directory=DB_DIR, embedding_function=OpenAIEmbeddings())
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(temperature=0.7, model_name=MODEL)
    
    return retriever, llm

def answer_query(query: str, retriever, llm) -> str:
    docs = retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in docs])
    answer = llm.invoke(f"Context: {context}\n\nQuestion: {query}")
    return str(answer)
    
if __name__ == "__main__":
    retriever, llm = create_rag_pipeline()
    
    print("💬 RAG Chatbot (type 'exit' to quit)\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit", "q"}:
            print("👋 Exiting...")
            break
        response = answer_query(query, retriever, llm)
        print(f"Bot: {response}\n")
