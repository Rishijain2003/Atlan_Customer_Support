import streamlit as st
import json

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
        # Display analysis section
        st.write("### 🔍 Internal Analysis (Support Team View)")
        st.write("**Topic:** (AI-generated)")
        st.write("**Sentiment:** (AI-generated)")
        st.write("**Priority:** (AI-generated)")

        st.write("### 💬 Final Response (Customer View)")
        st.write("This is where the AI-generated answer or routing message will appear.")

        # Add the new ticket to session state
        new_ticket = {
            "id": f"TICKET-{len(st.session_state.tickets)+1}",
            "subject": query[:50] + "..." if len(query) > 50 else query,
            "body": query
        }
        st.session_state.tickets.insert(0, new_ticket)  # insert at top
    else:
        st.warning("Please enter a query before analyzing.")

# -------------------------
# Dashboard Section (BELOW)
# -------------------------
st.subheader("📊 Bulk Ticket Classification Dashboard")
st.markdown(
    """
    All tickets are automatically ingested from the sample file.  
    Columns for AI-generated **Topic, Sentiment, and Priority** are left empty for now.
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
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

# Display all tickets from session state
for t in st.session_state.tickets:
    with st.expander(f"📝 {t['id']} — {t['subject']}"):
        st.write(f"**Body:** {t['body']}")
        st.write("**Topic:** (AI-generated)")
        st.write("**Sentiment:** (AI-generated)")
        st.write("**Priority:** (AI-generated)")

st.markdown("</div>", unsafe_allow_html=True)
