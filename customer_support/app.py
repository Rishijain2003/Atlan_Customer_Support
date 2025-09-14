import streamlit as st
import json
import os
#from customer_support_agent import run_graph  
from customer_support_agent import CustomerSupportAgent


BASE_DIR = os.path.dirname(__file__)  

SAMPLE_TICKETS_FILE = os.path.abspath(
    os.path.join(BASE_DIR, "..", "classifier", "sample_ticket_classified.json")
)

print("Looking for file at:", SAMPLE_TICKETS_FILE)

if os.path.exists(SAMPLE_TICKETS_FILE):
    with open(SAMPLE_TICKETS_FILE, "r", encoding="utf-8") as f:
        initial_tickets = json.load(f)
else:
    print(f"File not found: {SAMPLE_TICKETS_FILE}. Initializing empty ticket list.")
    initial_tickets = []


if "tickets" not in st.session_state:
    st.session_state.tickets = initial_tickets.copy()


# Page Config
st.set_page_config(page_title="AI Helpdesk Demo", layout="wide")
st.title("AI-Powered Helpdesk Demo")


# Interactive AI Agent Section
st.subheader("Interactive AI Agent")
st.markdown("Enter a new ticket or query below to see the AI pipeline in action:")

# Create a single agent instance (outside the form so it's reused)
agent = CustomerSupportAgent()
# Form for ticket input
with st.form("ticket_form", clear_on_submit=True):
    query = st.text_area(
        "New Ticket / Query",
        placeholder="Type your ticket here..."
    )

    submit_button = st.form_submit_button("Add ticket and Analyze")

    if submit_button and query.strip():
        with st.spinner("Processing your ticket..."):
            result = agent.run_graph(query)
            if "error" in result:
                st.error(f"Error occurred: {result['error']}")
            else:
                st.write("### Internal Analysis (Support Team View)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Topic", result.get("topic_tag", "N/A"))
                with col2:
                    st.metric("Sentiment", result.get("sentiment", "N/A"))
                with col3:
                    st.metric("Priority", result.get("priority", "N/A"))

                # Customer View
                st.write("### Final Response (Customer View)")
                if "answer" in result and result["answer"]:
                    st.write("**AI Response:**")
                    st.write(result["answer"].answer)
                    if hasattr(result["answer"], "sources") and result["answer"].sources:
                        with st.expander("Sources"):
                            for i, source in enumerate(result["answer"].sources, 1):
                                st.write(f"{i}. {source}")
                else:
                    st.write("AI-generated response will appear here.")

                # Add ticket to session state
                new_ticket = {
                    "id":  f"TICKET-{len(st.session_state.tickets)+245}",
                    "subject": result.get("subject", query[:50] + "..." if len(query) > 50 else query),
                    "body": result.get("body", query),
                    "topic_tag": result.get("topic_tag", ""),
                    "sentiment": result.get("sentiment", ""),
                    "priority": result.get("priority", "")
                }
                # st.session_state.tickets.insert(0, new_ticket)
                st.session_state.tickets.append(new_ticket)

                st.success("Ticket processed and added to dashboard!")
    elif submit_button:
        st.warning("Please enter a query before analyzing.")


# Dashboard Section
st.subheader("Bulk Ticket Classification Dashboard")
st.markdown(
    f"Displaying **{len(st.session_state.tickets)}** tickets. Processed tickets show AI-generated **Topic, Sentiment, and Priority**."
)

# Scrollable CSS
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


for t in reversed(st.session_state.tickets):
    topic = t.get('topic_tag', '')
    sentiment = t.get('sentiment', '')
    priority = t.get('priority', '')

    with st.expander(f"{t['id']} — {t['subject']}"):
        st.write(f"**Body:** {t['body']}")
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
