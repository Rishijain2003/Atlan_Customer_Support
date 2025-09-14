# Major Design Decisions and Trade-offs for the AI Pipeline

## Overview
The AI pipeline is designed to classify customer support tickets and route them to the appropriate team or generate relevant answers using a Retrieval-Augmented Generation (RAG) approach. Below, we outline the major design decisions and trade-offs made during the development of this pipeline.

---

## Design Decisions

### 1. **Classifier Node**
The pipeline begins with a classifier node that processes incoming tickets. The classifier uses a large language model (LLM) to analyze the ticket content and classify it into one or more topic tags. 

#### Key Features:
- **Input:** The classifier takes tickets from `sample_tickets.json`.
- **Prompt Design:** The LLM is provided with a detailed prompt that specifies how to handle various scenarios. This ensures that the classification is robust and context-aware.
- **Multiple Topic Tags:**
  - The problem statement did not specify whether a ticket should belong to one or multiple topic tags.
  - **Decision:** We opted for multiple topic tags as it made more sense in real-world scenarios where a ticket could span multiple topics. For example, a ticket might involve both "API/SDK" and "Product" issues.

#### Trade-offs:
- **Complexity vs. Simplicity:** Allowing multiple topic tags increases the complexity of the classification logic but provides a more nuanced understanding of the ticket.
- **Accuracy vs. Speed:** Classifying multiple tags may slightly increase processing time but ensures higher accuracy in routing.

---

### 2. **Routing Logic**
Once the topics are classified, the ticket is routed in real-time to either the RAG node or the `TicketRouter` node. The `TicketRouter` node ensures that the ticket is directed to the appropriate team based on the classified topics.

#### Key Features:
- **Dynamic Routing:** The routing logic dynamically determines the next step based on the classified topics.
- **Fallback Mechanism:** If no suitable subgraph is found, the ticket is routed to a default node.

#### Trade-offs:
- **Flexibility vs. Predictability:** Dynamic routing adds flexibility but requires robust error handling to manage edge cases.

---

### 3. **RAG Node**
The RAG node is responsible for generating answers using a Retrieval-Augmented Generation approach. This involves retrieving relevant documents and generating context-aware responses.

#### Key Features:
- **Model Choice:**
  - **OpenAI GPT-4-o-mini:** This model was chosen for its balance between performance and cost. It provides high-quality responses while being computationally efficient.
- **Embeddings Model:**
  - **OpenAI text-embedding-3-small:** This model was selected for generating embeddings due to its smaller size and efficiency, making it suitable for real-time applications.
- **Database:**
  - **Pinecone:** Pinecone was chosen as the vector database for its cloud-based architecture, scalability, and ease of integration.
- **Chunking Method:**
  - **Text Splitting:** Documents are split into chunks using the Recursive Character Text Splitter. This method ensures that the chunks are of manageable size (e.g., 1000 characters with 200-character overlap) for efficient retrieval and processing.

#### Trade-offs:
- **Model Performance vs. Cost:** While GPT-4-o-mini is not the most powerful model, it offers a good trade-off between performance and cost.
- **Embedding Size vs. Accuracy:** The smaller embedding model sacrifices some accuracy for faster processing and lower resource usage.
- **Database Choice:** Pinecone’s cloud-based nature ensures scalability but introduces dependency on external infrastructure.
- **Chunking:** Smaller chunks improve retrieval accuracy but increase the number of queries to the database.

---

## Conclusion
The design of this AI pipeline balances accuracy, efficiency, and scalability. Each decision, from allowing multiple topic tags to choosing specific models and databases, was made to ensure that the system meets real-world requirements while remaining cost-effective and robust. The trade-offs highlight the careful consideration given to each component to optimize the overall performance of the pipeline.
