import streamlit as st
from session_manager import SessionManager
from agents.orchestrator import Orchestrator
from models import FinalVeoPrompt
from jinja2 import Environment, FileSystemLoader
from config import Config

# Set page config to wide mode
st.set_page_config(layout="wide")

st.title("VeoPrompt-Pro: Agentic Video Prompt Engineering UI")

# Check API key status
google_key = Config.get_google_api_key()
anthropic_key = Config.get_anthropic_api_key()

# Display API key status in a more compact way
api_col1, api_col2 = st.columns(2)
with api_col1:
    if google_key:
        st.success("✅ Google API Key: Set")
    else:
        st.error("❌ Google API Key: Not Set")
with api_col2:
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
if 'generated_prompt' not in st.session_state:
    st.session_state['generated_prompt'] = None

# Create main two-column layout
input_col, output_col = st.columns([1, 1], gap="large")
AREA_HEIGHT = 100
# Left column - Inputs
with input_col:
    st.subheader("Scene Details")

    # Character input
    character_input = st.text_area(
        "Character Description",
        placeholder="Describe the main character (e.g., 'Bigfoot, a large hairy creature with friendly eyes')",
        height=AREA_HEIGHT
    )

    # Scene input
    scene_input = st.text_area(
        "Scene Setting",
        placeholder="Describe the scene location and environment (e.g., 'Dense jungle with tall trees and vines')",
        height=AREA_HEIGHT
    )

    # Action input
    action_input = st.text_area(
        "Core Action & Dialogue",
        placeholder="Describe what's happening and any dialogue (e.g., 'Bigfoot is tired of the beatboxing fish and covers his ears')",
        height=AREA_HEIGHT
    )

    # Camera style input
    camera_style = st.text_area(
        "Camera Style",
        placeholder="e.g., 'Handheld, close-up shots, natural movement'",
        height=AREA_HEIGHT
    )

    # Sounds input
    sounds_input = st.text_area(
        "Sounds & Audio",
        placeholder="List the sounds in the scene (e.g., 'Beatboxing sounds, rustling leaves, Bigfoot's grunts')",
        height=AREA_HEIGHT
    )

    # Landscape input
    landscape_input = st.text_area(
        "Landscape Details",
        placeholder="Describe the landscape and environment details (e.g., 'Moss-covered rocks, flowing stream, dense foliage')",
        height=AREA_HEIGHT
    )

    # Props input
    props_input = st.text_area(
        "Props & Objects",
        placeholder="List any props or objects in the scene (e.g., 'Fishing rod, backpack, camera equipment')",
        height=AREA_HEIGHT
    )

# Right column - Generate button and output
with output_col:
    st.subheader("Generate")
    generate_button = st.button("🚀 Generate Veo Prompt", type="primary", use_container_width=True)

    # Process inputs when generate button is clicked
    if generate_button:
        if not character_input.strip() and not scene_input.strip() and not action_input.strip():
            st.error("Please provide at least character, scene, or action details.")
        else:
            with st.spinner("Processing and enriching your inputs..."):
                try:
                    # Create structured inputs dictionary
                    structured_inputs = {
                        'character': character_input.strip(),
                        'scene': scene_input.strip(),
                        'action': action_input.strip(),
                        'camera_style': camera_style.strip(),
                        'sounds': sounds_input.strip(),
                        'landscape': landscape_input.strip(),
                        'props': props_input.strip()
                    }

                    # Process through the orchestrator
                    final_prompt: FinalVeoPrompt = st.session_state['orchestrator'].process_user_input(structured_inputs)

                    # Render with Jinja2 template
                    env = Environment(loader=FileSystemLoader('templates'))
                    template = env.get_template('veoprompt.md.j2')
                    prompt_md = template.render(**final_prompt.model_dump())

                    # Store in session state
                    st.session_state['generated_prompt'] = prompt_md

                except Exception as e:
                    st.error(f"Error generating prompt: {e}")
                    st.info("Try providing more detailed inputs or check your API keys.")

    # Display the generated prompt if available
    if st.session_state['generated_prompt']:
        # Create a row with title and copy button
        title_col, copy_col = st.columns([3, 1])
        with title_col:
            st.markdown("### Generated Veo Prompt")
        with copy_col:
            # Create a copy button that actually copies to clipboard
            st.text_area(
                "Copy to clipboard",
                value=st.session_state['generated_prompt'],
                height=1,
                key="clipboard_area",
                label_visibility="collapsed"
            )
            if st.button("📋 Copy", key="copy_button", use_container_width=True):
                st.success("✅ Copied to clipboard!")

        st.markdown("---")
        st.markdown(st.session_state['generated_prompt'])