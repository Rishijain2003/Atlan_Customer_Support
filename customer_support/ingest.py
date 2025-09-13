import json
import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)

BASE_DIR = "data/vector_store"
DEV_DB = os.path.join(BASE_DIR, "developer_db")
DOC_DB = os.path.join(BASE_DIR, "atlan_document_db")

from dotenv import load_dotenv

    
def build_vector_db(url_file: str, db_dir: str):
    """Build a vector database from a list of URLs into a given directory."""
    load_dotenv()

    os.environ['OPENAI_API_KEY'] = os.getenv('Openai_api_key')
    with open(url_file) as f:
        urls = json.load(f)

    logger.info(f"🌐 Loading {len(urls)} URLs from {url_file} ...")
    loader = WebBaseLoader(urls)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=db_dir)

    logger.info(f"✅ Stored {len(chunks)} chunks in {db_dir}")


if __name__ == "__main__":
    # Developer-related DB
    logger.info("📦 Building Developer Vector DB...")
    build_vector_db("data/development_urls.json", DEV_DB)

    # Document/FAQ-related DB
    logger.info("📦 Building Document Vector DB...")
    build_vector_db("data/document_urls.json", DOC_DB)
