retriever_content = """
You are a helpful assistant. Use the following pieces of retrieved context to answer the question.
If you don't know the answer from the context, just say: "I don't know." Do not make up an answer.
In case you get context in a programming language try to format it properly in your answer.
If Context is empty then return I dont Know and dont make up your own answer without getting the context here



Question: {question}

Source urls: {source}
Context:
{context}

"""

ticket_structure = """
You are an AI assistant that converts user queries into structured support tickets.

Input question: {question}

Your task:
1. Keep the body exactly as the input question.
2. Generate a concise, clear subject line (1 sentence max).
3. Assign a unique ticket ID in the format: "TICKET-<number>".
   - Use a random 4-digit number (e.g., TICKET-1245).

Example:
Input: "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing..."

Output should be a JSON object with:
- id: "TICKET-1245"
- subject: "Snowflake connection failing - need setup help"  
- body: "Hi team, we're trying to set up our primary Snowflake production database..." (exact input)

Please return only the structured ticket information.
"""

classification_prompt = """
You are an AI assistant that classifies customer support tickets for Atlan.

Ticket ID: {id}
Subject: {subject}
Body: {body}

Your task:
1. Carefully read the subject and body.
2. Assign exactly ONE Topic Tag from this list (choose the single best fit):
   - How-to → Questions about how to use a feature
   - Product → General product functionality
   - Connector → Issues or setup with external systems (Snowflake, Redshift, Airflow, etc.)
   - Lineage → Questions or problems related to lineage capture and display
   - API/SDK → Questions about APIs, SDKs, or programmatic use
   - SSO → Authentication and Single Sign-On related issues
   - Glossary → Business glossary and metadata governance
   - Best practices → Catalog hygiene, scaling, or recommendations
   - Sensitive data → PII, security, access control

3. Assign Sentiment from: Frustrated, Curious, Angry, Neutral.

4. Assign Priority:
   - P0 → Business critical or urgent blockers
   - P1 → Important but not blocking immediate business
   - P2 → General guidance, learning, or lower urgency

Please return only the classification information.
"""