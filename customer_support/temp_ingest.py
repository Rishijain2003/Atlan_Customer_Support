import json
import os
import logging
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("Openai_api_key")

def build_vector_db(url_file: str, index_name: str):
    """Build a vector database from a list of URLs into Pinecone."""
    # Init Pinecone client
    pc = Pinecone(api_key=os.getenv("pinecone_api_key"))
    env = os.getenv("PINECONE_ENV")

    # Create index if not exists
    if index_name not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings size
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=env)
        )
        logger.info(f"📦 Created Pinecone index `{index_name}` in {env}")

    # Load URLs
    with open(url_file) as f:
        urls = json.load(f)

    logger.info(f"🌐 Loading {len(urls)} URLs from {url_file} ...")
    loader = WebBaseLoader(urls)
    docs = loader.load()

    # Split documents
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # Create embeddings + push to Pinecone
    embeddings = OpenAIEmbeddings()
    vectordb = PineconeVectorStore.from_documents(
        chunks,
        embeddings,
        index_name=index_name
    )

    logger.info(f"✅ Stored {len(chunks)} chunks in Pinecone index `{index_name}`")


if __name__ == "__main__":
    logger.info("📦 Building Developer Vector DB...")
    build_vector_db("data/temp.json", "tempdb")

    # logger.info("📦 Building Document Vector DB...")
    # build_vector_db("data/document_urls.json", "document-db")
