import streamlit as st
from session_manager import SessionManager
from agents.orchestrator import Orchestrator
from models import FinalVeoPrompt
from jinja2 import Environment, FileSystemLoader
from config import Config

# Set page config to wide mode
st.set_page_config(layout="wide")

st.title("VeoPrompt-Pro: Generate Professional Vlog Prompts")
st.markdown("*Transform minimal inputs into rich, detailed YouTube vlog prompts like 'Outdoor Boys' channel*")

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
        st.info("ℹ️ Anthropic API Key: Optional")

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

# Left column - Simplified Inputs
with input_col:
    st.subheader("✨ Quick Start - Minimal Inputs")
    st.markdown("*Fill just 1-3 fields below for a complete professional prompt*")

    # Essential inputs - these are the core ones
    character_input = st.text_area(
        "🎭 Character (Required)",
        placeholder="e.g., 'Bigfoot', 'A friendly Yeti', 'Outdoor enthusiast'",
        height=80,
        help="Describe the main character - can be as simple as 'Bigfoot' or detailed"
    )

    scene_input = st.text_area(
        "🏞️ Scene/Action",
        placeholder="e.g., 'Building a snow kitchen', 'Finding an alien's selfie stick', 'Camping in the forest'",
        height=80,
        help="What's happening in the scene? Keep it simple - the AI will add rich details"
    )

    # Optional detailed inputs - collapsible
    with st.expander("🔧 Optional Details (Advanced)", expanded=False):
        st.markdown("*Only fill these if you want specific control over these elements*")

        action_input = st.text_area(
            "💬 Specific Dialogue/Actions",
            placeholder="e.g., 'Says: Snow sandwiches are the ultimate mountain snack!'",
            height=70
        )

        camera_style = st.text_area(
            "📹 Camera Style",
            placeholder="e.g., 'POV selfie stick, handheld'",
            height=70
        )

        sounds_input = st.text_area(
            "🔊 Sounds",
            placeholder="e.g., 'Crunching snow, laughter, mountain echoes'",
            height=70
        )

        landscape_input = st.text_area(
            "🌲 Landscape Details",
            placeholder="e.g., 'Snowy mountains, pine trees'",
            height=70
        )

        props_input = st.text_area(
            "🎯 Props/Objects",
            placeholder="e.g., 'Pinecones, icicles, snowballs'",
            height=70
        )

    # Examples for inspiration
    with st.expander("💡 Example Ideas", expanded=False):
        st.markdown("""
        **Quick Examples:**
        - Character: "Yeti and Bigfoot" + Scene: "Building snow sandwiches"
        - Character: "Friendly explorer" + Scene: "Discovering alien technology"
        - Character: "Bigfoot" + Scene: "Camping in cozy forest shelter"
        - Character: "Outdoor enthusiast" + Scene: "Winter campfire cooking"

        **The AI will automatically add:**
        - Rich character descriptions and personalities
        - Detailed atmospheric settings
        - Professional camera work and timing
        - Authentic vlog-style dialogue
        - Complete sound design
        - Natural props and environment details
        """)

# Right column - Generate button and output
with output_col:
    st.subheader("🚀 Generate Professional Prompt")

    # Show what's required
    if not character_input.strip():
        st.info("💡 **Tip:** Add at least a character description to get started!")
    else:
        st.success("✅ Ready to generate!")

    generate_button = st.button(
        "🚀 Generate Professional Vlog Prompt",
        type="primary",
        use_container_width=True,
        disabled=not character_input.strip()
    )

    # Process inputs when generate button is clicked
    if generate_button:
        with st.spinner("🎬 Creating your professional vlog prompt..."):
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
                st.success("✅ Professional prompt generated!")

            except Exception as e:
                st.error(f"❌ Error generating prompt: {e}")
                st.info("💡 Try simplifying your inputs or check the character description.")

    # Display the generated prompt if available
    if st.session_state['generated_prompt']:
        # Create a row with title and copy button
        title_col, copy_col = st.columns([3, 1])
        with title_col:
            st.markdown("### 🎥 Your Professional Vlog Prompt")
        with copy_col:
            if st.button("📋 Copy Prompt", key="copy_button", use_container_width=True):
                st.code(st.session_state['generated_prompt'], language="markdown")
                st.success("✅ Copied!")

        # Show the prompt in a nice container
        with st.container():
            st.markdown("---")
            st.markdown(st.session_state['generated_prompt'])
            st.markdown("---")
            st.markdown("*💡 This prompt is optimized for VEO3 and other AI video generation models*")