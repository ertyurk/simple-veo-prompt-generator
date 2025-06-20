import streamlit as st
from session_manager import SessionManager
from agents.orchestrator import Orchestrator
from models import FinalVeoPrompt, MultiScenePrompt, VideoScene
from jinja2 import Environment, FileSystemLoader
from config import Config

# Set page config to wide mode
st.set_page_config(layout="wide")

st.title("VeoPrompt-Pro: Multi-Scene Vlog Generator")
st.markdown("*Create multiple 8-second scenes for up to 40-second professional vlogs*")

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
if 'video_scenes' not in st.session_state:
    st.session_state['video_scenes'] = [{}]  # Start with one empty scene
if 'generated_prompts' not in st.session_state:
    st.session_state['generated_prompts'] = None

# Helper function to create scene input fields
def create_scene_input(scene_num, scene_data):
    """Create input fields for a single video scene"""

    with st.expander(f"🎬 Video {scene_num} (8 seconds)", expanded=scene_num == 1):
        col1, col2 = st.columns(2)

        with col1:
            character = st.text_area(
                f"🎭 Character - Video {scene_num}",
                value=scene_data.get('character', ''),
                placeholder="e.g., 'Bigfoot', 'A friendly Yeti', 'Outdoor enthusiast'",
                height=80,
                key=f"character_{scene_num}",
                help="Main character(s) for this scene"
            )

            scene_setting = st.text_area(
                f"🏞️ Scene Setting - Video {scene_num}",
                value=scene_data.get('scene_setting', ''),
                placeholder="e.g., 'Snowy mountain landscape', 'Dense forest clearing'",
                height=80,
                key=f"scene_setting_{scene_num}",
                help="Location and environment for this scene"
            )

            action_dialogue = st.text_area(
                f"💬 Action & Dialogue - Video {scene_num}",
                value=scene_data.get('action_dialogue', ''),
                placeholder="e.g., 'Building snow sandwiches and laughing together'",
                height=80,
                key=f"action_dialogue_{scene_num}",
                help="What happens in this 8-second scene"
            )

            camera_style = st.text_area(
                f"📹 Camera Style - Video {scene_num}",
                value=scene_data.get('camera_style', ''),
                placeholder="e.g., 'POV selfie stick, handheld, close-up shots'",
                height=70,
                key=f"camera_style_{scene_num}",
                help="Camera movement and shot types"
            )

        with col2:
            sounds = st.text_area(
                f"🔊 Sounds - Video {scene_num}",
                value=scene_data.get('sounds', ''),
                placeholder="e.g., 'Crunching snow, laughter, mountain echoes'",
                height=80,
                key=f"sounds_{scene_num}",
                help="Audio elements for this scene"
            )

            landscape = st.text_area(
                f"🌲 Landscape - Video {scene_num}",
                value=scene_data.get('landscape', ''),
                placeholder="e.g., 'Snow-covered pine trees, rugged mountains'",
                height=80,
                key=f"landscape_{scene_num}",
                help="Environmental details"
            )

            props = st.text_area(
                f"🎯 Props - Video {scene_num}",
                value=scene_data.get('props', ''),
                placeholder="e.g., 'Pinecones, icicles, snowballs'",
                height=80,
                key=f"props_{scene_num}",
                help="Objects and items in the scene"
            )

        # Delete button (only show if more than 1 scene)
        if len(st.session_state['video_scenes']) > 1:
            if st.button(f"🗑️ Delete Video {scene_num}", key=f"delete_{scene_num}", type="secondary"):
                return "DELETE"

    return {
        'character': character,
        'scene_setting': scene_setting,
        'action_dialogue': action_dialogue,
        'camera_style': camera_style,
        'sounds': sounds,
        'landscape': landscape,
        'props': props
    }

# Main layout
st.markdown("---")

# Scene management buttons
button_col1, button_col2, button_col3 = st.columns([1, 1, 2])

with button_col1:
    if st.button("➕ Add Video Scene", type="secondary", disabled=len(st.session_state['video_scenes']) >= 5):
        st.session_state['video_scenes'].append({})
        st.rerun()

with button_col2:
    st.markdown(f"**Total Duration:** {len(st.session_state['video_scenes']) * 8} seconds")

with button_col3:
    if len(st.session_state['video_scenes']) >= 5:
        st.info("Maximum 5 scenes (40 seconds) reached")

# Create input fields for all scenes
scenes_to_delete = []
updated_scenes = []

for i, scene_data in enumerate(st.session_state['video_scenes']):
    scene_num = i + 1
    result = create_scene_input(scene_num, scene_data)

    if result == "DELETE":
        scenes_to_delete.append(i)
    else:
        updated_scenes.append(result)

# Handle deletions
if scenes_to_delete:
    for idx in reversed(scenes_to_delete):  # Delete from end to avoid index issues
        del st.session_state['video_scenes'][idx]
    st.rerun()
else:
    st.session_state['video_scenes'] = updated_scenes

# Generate button and consistency settings
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 Story Consistency")

    overall_story = st.text_area(
        "📖 Overall Story/Theme",
        placeholder="e.g., 'Bigfoot and Yeti having winter outdoor adventures'",
        height=80,
        help="Common theme that connects all video scenes"
    )

    main_characters = st.text_input(
        "👥 Main Characters (consistent across scenes)",
        placeholder="e.g., 'Bigfoot, Yeti'",
        help="Characters that appear throughout the video series"
    )

with col2:
    st.subheader("🚀 Generate Multi-Scene Prompts")

    # Check if at least one scene has character info
    has_content = any(scene.get('character', '').strip() for scene in st.session_state['video_scenes'])

    if not has_content:
        st.info("💡 Add character info to at least one scene to get started!")
    else:
        st.success(f"✅ Ready to generate {len(st.session_state['video_scenes'])} video scenes!")

    generate_button = st.button(
        f"🚀 Generate {len(st.session_state['video_scenes'])} Professional Prompts",
        type="primary",
        use_container_width=True,
        disabled=not has_content
    )

# Process inputs when generate button is clicked
if generate_button:
    with st.spinner(f"🎬 Creating {len(st.session_state['video_scenes'])} professional video prompts..."):
        try:
            # Create multi-scene data
            multi_scene_data = {
                'overall_story': overall_story.strip(),
                'main_characters': main_characters.strip(),
                'video_scenes': st.session_state['video_scenes']
            }

            # Process through the orchestrator
            multi_scene_prompts = st.session_state['orchestrator'].process_multi_scene_input(multi_scene_data)

            # Store in session state
            st.session_state['generated_prompts'] = multi_scene_prompts
            st.success(f"✅ {len(st.session_state['video_scenes'])} professional prompts generated!")

        except Exception as e:
            st.error(f"❌ Error generating prompts: {e}")
            st.info("💡 Try simplifying your inputs or check the character descriptions.")

# Display the generated prompts if available
if st.session_state['generated_prompts']:
    st.markdown("---")

    # Create a row with title and copy button
    title_col, copy_col = st.columns([3, 1])
    with title_col:
        st.markdown("### 🎥 Your Multi-Scene Professional Prompts")
    with copy_col:
        if st.button("📋 Copy All Prompts", key="copy_all_button", use_container_width=True):
            st.code(st.session_state['generated_prompts'], language="markdown")
            st.success("✅ All prompts copied!")

    # Show the prompts in a nice container
    with st.container():
        st.markdown(st.session_state['generated_prompts'])
        st.markdown("---")
        st.markdown("*💡 Each prompt is optimized for VEO3 and other AI video generation models*")