import streamlit as st
from langchain_groq import ChatGroq
from together import Together
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")

# Initialize models
llm = ChatGroq(
    model_name="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=300
)
together_client = Together(api_key=os.environ["TOGETHER_API_KEY"])

# Functions for generating manga story and storyboard image
def generate_manga_story(prompt, genre):
    messages = [
        ("system", f"""You're a manga storytelling AI. Create a {genre} manga with:
        - 3-5 panels
        - Expressive character dialogues (e.g., *shouting*, *gasping*)
        - Action descriptions in [brackets]
        - Maintain manga pacing and page flow."""),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def generate_storyboard_image(description):
    """Generate manga-style image using Together's FLUX model"""
    try:
        # Crafting a manga-specific prompt
        prompt = (
            f"Manga-style illustration: {description}, "
            "monochrome, clean line art, dynamic pose, expressive facial features, "
            "sharp details, screentone shading, speech bubble with dialogue, "
            "high contrast, professional manga panel style."
        )
        
        # Generate the image
        response = together_client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=4
        )
        
        # Use the URL field from the response
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

# Streamlit UI
# Main content layout
st.title("MANGA - AI")


# Sidebar for input
with st.sidebar:
    st.header("Input Details")
    manga_prompt = st.text_area("Manga Prompt", "Two high school students, Taki from Tokyo and Mitsuha from a rural town, mysteriously switch bodies. Communicating through messages, they develop feelings for each other. As they try to meet, a shocking truth unfolds, testing love, fate, and destiny.")
    genre = st.selectbox("Genre", ["Romance", "Action", "Fantasy", "Sci-Fi", "Horror"])
    storyboard_desc = st.text_area("Storyboard Image Description", "")
    if st.button("Generate Storyboard Image"):
        if storyboard_desc.strip():
            storyboard_image = generate_storyboard_image(storyboard_desc)
            if storyboard_image:
                st.session_state.storyboard_images.append((storyboard_desc, storyboard_image))
        else:
            st.warning("Please provide a description for the storyboard image.")

# Initialize session state
if "manga_story" not in st.session_state:
    st.session_state.manga_story = None
if "prompt_image" not in st.session_state:
    st.session_state.prompt_image = None
if "storyboard_images" not in st.session_state:
    st.session_state.storyboard_images = []

# Generate manga story and prompt image
if st.button("Generate Manga Story"):
    st.session_state.manga_story = generate_manga_story(manga_prompt, genre)
    st.session_state.prompt_image = generate_storyboard_image(manga_prompt)

# Streamlit UI
#st.set_page_config(page_title="Generative MANGA", layout="wide", initial_sidebar_state="expanded")

st.subheader("Generate Your Manga Story and Visual Storyboard")
#st.markdown("### Generate Your Manga Story and Visual Storyboard")

# Display manga story and generated content
if st.session_state.manga_story or st.session_state.prompt_image or st.session_state.storyboard_images:
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.subheader("Generated Manga Story")
        if st.session_state.manga_story:
            st.text_area("Manga Story", value=st.session_state.manga_story, height=400, label_visibility="collapsed")
    
    with col2:
        st.subheader("Generated Manga Illustration")
        if st.session_state.prompt_image:
            st.image(st.session_state.prompt_image, caption="Manga Illustration", use_container_width=True)

# Display storyboard descriptions and images in sequence
if st.session_state.storyboard_images:
    for idx, (desc, img_url) in enumerate(st.session_state.storyboard_images):
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            st.markdown(f"**Panel {idx + 1} Description:** {desc}")
        
        with col2:
            st.image(img_url, caption=f"Storyboard Panel {idx + 1}", use_container_width=True)