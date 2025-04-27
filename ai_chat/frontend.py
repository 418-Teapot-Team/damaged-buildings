import streamlit as st
import requests
import uuid

# Streamlit page configuration
st.set_page_config(
    page_title="AI Chat for Identifying Destroyed Possessions",
    layout="wide"
)

# Flask backend URL (update if hosted elsewhere)
BACKEND_URL = "http://localhost:5000"

# Generate or retrieve a unique user ID for the session
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Initialize session state for agent configuration and messages
if 'agent_config' not in st.session_state:
    st.session_state.agent_config = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to get or create an agent on the backend
@st.cache_data(show_spinner=False)
def get_agent_config(user_id):
    response = requests.post(
        f"{BACKEND_URL}/get-agent",
        json={"user_id": user_id}
    )
    data = response.json()
    if data.get('status') == 'success':
        return data['message']
    else:
        st.error(f"Error initializing agent: {data.get('message')}")
        return None

# Function to send a user message and get AI response
def send_message_to_backend(user_id, user_message, config):
    payload = {
        "user_id": user_id,
        "user_message": user_message,
        "config": config
    }
    response = requests.post(
        f"{BACKEND_URL}/answer-question",
        json=payload
    )
    data = response.json()
    if data.get('status') == 'success':
        return data['message']
    else:
        st.error(f"Error: {data.get('message')}")
        return None

# Initialize agent config at startup
if st.session_state.agent_config is None:
    with st.spinner('Initializing AI agent...'):
        config = get_agent_config(st.session_state.user_id)
        st.session_state.agent_config = config

# Title and instructions
st.title("AI Chat for Identifying Destroyed Possessions and Calculating Repayment Value")
st.write("Describe your destroyed possessions, and the AI will help calculate repayment value.")

# Display chat messages
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**AI:** {msg['content']}")

# User input form
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Your message:")
    submit = st.form_submit_button("Send")

# Handle form submission
if submit and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send to backend
    with st.spinner('AI is thinking...'):
        ai_response = send_message_to_backend(
            st.session_state.user_id,
            user_input,
            st.session_state.agent_config
        )

    # Append AI response
    if ai_response is not None:
        st.session_state.messages.append({"role": "ai", "content": ai_response})

    # Rerun to display updated chat
    st.rerun()
