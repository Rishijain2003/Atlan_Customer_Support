import streamlit as st
import json
from temp_parent2 import run_graph  # Import the main function from temp_parent2.py

# -------------------------
# Load sample tickets
# -------------------------
SAMPLE_TICKETS_FILE = "sample_tickets.json"

with open(SAMPLE_TICKETS_FILE, "r", encoding="utf-8") as f:
    initial_tickets = json.load(f)

# Initialize session state for tickets
if "tickets" not in st.session_state:
    st.session_state.tickets = initial_tickets.copy()

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="AI Helpdesk Demo", layout="wide")
st.title("📩 AI-Powered Helpdesk Demo")

# -------------------------
# Interactive AI Agent Section (TOP)
# -------------------------
st.subheader("🤖 Interactive AI Agent")
st.markdown("Enter a new ticket or query below to see the AI pipeline in action:")

query = st.text_area("✍️ New Ticket / Query", placeholder="Type your ticket here...")

if st.button("Analyze Ticket"):
    if query.strip():
        with st.spinner("Processing your ticket..."):
            # Call the graph with the query
            result = run_graph(query)
            
            # Check for errors
            if "error" in result:
                st.error(f"Error occurred: {result['error']}")
            else:
                # Display analysis section
                st.write("### 🔍 Internal Analysis (Support Team View)")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Topic", result.get("topic_tag", "N/A"))
                with col2:
                    sentiment = result.get("sentiment", "N/A")
                    st.metric("Sentiment", sentiment)
                with col3:
                    priority = result.get("priority", "N/A")
                    st.metric("Priority", priority)

                st.write("### 💬 Final Response (Customer View)")
                
                # Display RAG response
                if "answer" in result and result["answer"]:
                    st.write("**AI Response:**")
                    st.write(result["answer"].answer)
                    
                    if hasattr(result["answer"], 'sources') and result["answer"].sources:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(result["answer"].sources, 1):
                                st.write(f"{i}. {source}")
                else:
                    st.write("AI-generated response will appear here.")

                # Add the new ticket to session state
                new_ticket = {
                    "id": result.get("id", f"TICKET-{len(st.session_state.tickets)+1}"),
                    "subject": result.get("subject", query[:50] + "..." if len(query) > 50 else query),
                    "body": result.get("body", query),
                    "topic_tag": result.get("topic_tag", ""),
                    "sentiment": result.get("sentiment", ""),
                    "priority": result.get("priority", "")
                }
                st.session_state.tickets.insert(0, new_ticket)  # insert at top
                
                st.success("✅ Ticket processed and added to dashboard!")
    else:
        st.warning("Please enter a query before analyzing.")

# -------------------------
# Dashboard Section (BELOW)
# -------------------------
st.subheader("📊 Bulk Ticket Classification Dashboard")
st.markdown(
    f"""
    Displaying **{len(st.session_state.tickets)}** tickets.
    Processed tickets show AI-generated **Topic, Sentiment, and Priority**.
    """
)

# Add scrollable area with styled CSS
st.markdown(
    """
    <style>
    .scroll-box {
        max-height: 400px;
        overflow-y: auto;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .ai-generated {
        color: #28a745;
        font-weight: bold;
    }
    .placeholder {
        color: #6c757d;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

# Display all tickets from session state
for t in st.session_state.tickets:
    topic = t.get('topic_tag', '')
    sentiment = t.get('sentiment', '')
    priority = t.get('priority', '')
    
    with st.expander(f"📝 {t['id']} — {t['subject']}"):
        st.write(f"**Body:** {t['body']}")
        
        # Show AI-generated fields or placeholders
        if topic:
            st.markdown(f'**Topic:** <span class="ai-generated">{topic}</span>', unsafe_allow_html=True)
        else:
            st.markdown('**Topic:** <span class="placeholder">(AI-generated)</span>', unsafe_allow_html=True)
            
        if sentiment:
            st.markdown(f'**Sentiment:** <span class="ai-generated">{sentiment}</span>', unsafe_allow_html=True)
        else:
            st.markdown('**Sentiment:** <span class="placeholder">(AI-generated)</span>', unsafe_allow_html=True)
            
        if priority:
            st.markdown(f'**Priority:** <span class="ai-generated">{priority}</span>', unsafe_allow_html=True)
        else:
            st.markdown('**Priority:** <span class="placeholder">(AI-generated)</span>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)