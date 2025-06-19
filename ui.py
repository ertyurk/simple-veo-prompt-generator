import streamlit as st
from session_manager import SessionManager
from agents.orchestrator import Orchestrator
from models import FinalVeoPrompt
from jinja2 import Environment, FileSystemLoader
from config import Config

st.title("VeoPrompt-Pro: Agentic Video Prompt Engineering UI")

# Check API key status
google_key = Config.get_google_api_key()
anthropic_key = Config.get_anthropic_api_key()

# Display API key status
col1, col2 = st.columns(2)
with col1:
    if google_key:
        st.success("✅ Google API Key: Set")
    else:
        st.error("❌ Google API Key: Not Set")
with col2:
    if anthropic_key:
        st.success("✅ Anthropic API Key: Set")
    else:
        st.error("❌ Anthropic API Key: Not Set")

if not google_key:
    st.warning("⚠️ Please set the GOOGLE_API_KEY environment variable to use this application.")
    st.stop()

# Initialize session state
if 'session_manager' not in st.session_state:
    st.session_state['session_manager'] = SessionManager()
if 'orchestrator' not in st.session_state:
    st.session_state['orchestrator'] = Orchestrator(st.session_state['session_manager'])

user_input = st.text_area("Describe your scene or video idea:")
submit = st.button("Generate Prompt")

if submit and user_input:
    with st.spinner("Processing your request..."):
        try:
            final_prompt: FinalVeoPrompt = st.session_state['orchestrator'].process_user_input(user_input)
            # Render with Jinja2 template
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('veoprompt.md.j2')
            prompt_md = template.render(**final_prompt.model_dump())
            st.subheader("Generated Veo Prompt:")
            st.markdown(prompt_md)
        except Exception as e:
            st.error(f"Error: {e}")