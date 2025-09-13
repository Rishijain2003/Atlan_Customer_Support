import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

BASE_DIR = "data/vector_store"

TEMP_DB = os.path.join(BASE_DIR, "temp_db")
from dotenv import load_dotenv

def build_vector_db(url_file: str, db_dir: str):
    """Build a vector database from a list of URLs into a given directory."""
    with open(url_file) as f:
        urls = json.load(f)
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    MODEL = "gpt-4o-mini"
    print(f"🌐 Loading {len(urls)} URLs from {url_file} ...")
    loader = WebBaseLoader(urls)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=db_dir)

    print(f"✅ Stored {len(chunks)} chunks in {db_dir}")


if __name__ == "__main__":
    # Developer-related DB
    build_vector_db("data/temp.json", TEMP_DB)

    
