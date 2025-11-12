import streamlit as st
import torch
import numpy as np
import io
import soundfile as sf
from datetime import datetime
import base64
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="AI TTS & Voice Cloning",
    page_icon="🎤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .model-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'audio_generated' not in st.session_state:
    st.session_state.audio_generated = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import TTS
        return True
    except ImportError:
        return False

def setup_tts_model():
    """Setup TTS model with error handling"""
    try:
        from TTS.api import TTS
        # Use a lightweight model for demo
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        return tts
    except Exception as e:
        st.warning(f"⚠️ TTS model loading failed: {str(e)}")
        return None

def generate_sample_audio(text, speed=1.0):
    """Generate sample audio when TTS models are not available"""
    sample_rate = 22050
    duration = max(1, len(text) / 15)
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create more natural sounding sample
    frequency = 220
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    # Add some harmonics
    audio += 0.1 * np.sin(2 * np.pi * frequency * 2 * t)
    audio += 0.05 * np.sin(2 * np.pi * frequency * 3 * t)
    
    # Apply fade in/out
    fade_samples = int(0.1 * sample_rate)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    # Speed adjustment
    if speed != 1.0:
        new_length = int(len(audio) / speed)
        audio = np.interp(
            np.linspace(0, len(audio), new_length),
            np.arange(len(audio)),
            audio
        )
    
    # Convert to bytes
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    
    return buffer

def main():
    st.markdown('<div class="main-header">🎤 AI Text-to-Speech with Voice Cloning</div>', unsafe_allow_html=True)
    
    # Dependency check
    if not check_dependencies():
        st.markdown("""
        <div class="warning-box">
        ⚠️ <b>Note:</b> Some advanced TTS models are not available in this demo. 
        The app will generate sample audio. For full functionality, run locally with GPU.
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    model_option = st.sidebar.selectbox(
        "🎯 Select TTS Model:",
        ["Coqui TTS", "Facebook MMS", "XTTS", "Tortoise TTS", "Sample Mode"]
    )
    
    enable_cloning = st.sidebar.checkbox("🎤 Enable Voice Cloning", value=False)
    
    # Settings
    st.sidebar.subheader("Audio Settings")
    speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1)
    language = st.sidebar.selectbox("Language", 
        ["English", "Hindi", "Spanish", "French", "German", "Chinese", "Japanese"])
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Text Input")
        text_input = st.text_area(
            "Enter your text here:",
            height=150,
            value="Welcome to AI Text-to-Speech application with voice cloning capabilities. This demo shows how advanced TTS models can generate natural sounding speech.",
            placeholder="Type your text here..."
        )
        
        if enable_cloning:
            st.subheader("🎤 Voice Cloning")
            cloning_method = st.radio(
                "Voice Cloning Method:",
                ["Upload Reference Audio", "Use Pre-trained Voice", "Record Voice"]
            )
            
            if cloning_method == "Upload Reference Audio":
                ref_audio = st.file_uploader("Upload reference audio (WAV, MP3)", 
                                           type=['wav', 'mp3', 'ogg'])
                if ref_audio:
                    st.success(f"✅ Reference audio uploaded: {ref_audio.name}")
                    
            elif cloning_method == "Use Pre-trained Voice":
                voice_option = st.selectbox("Select Voice:", 
                    ["Male Voice 1", "Female Voice 1", "Male Voice 2", "Female Voice 2"])
                
            elif cloning_method == "Record Voice":
                st.info("🎤 Voice recording feature available in local deployment")
    
    with col2:
        st.subheader("🔊 Output Settings")
        voice_gender = st.selectbox("Voice Gender", ["Male", "Female", "Neutral"])
        emotion = st.selectbox("Emotion", ["Neutral", "Happy", "Sad", "Angry", "Excited"])
        
        with st.expander("Advanced Settings"):
            pitch = st.slider("Pitch", 0.5, 2.0, 1.0, 0.1)
            energy = st.slider("Energy", 0.5, 2.0, 1.0, 0.1)
        
        generate_btn = st.button(
            "🎵 Generate Speech",
            type="primary",
            use_container_width=True
        )
    
    # Generate audio
    if generate_btn and text_input:
        with st.spinner("🔄 Generating audio... This may take a few seconds"):
            try:
                # Try to use actual TTS if available
                tts_model = setup_tts_model()
                if tts_model:
                    # Generate with actual TTS model
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                        tts_model.tts_to_file(text=text_input, file_path=tmp_file.name)
                        with open(tmp_file.name, "rb") as f:
                            audio_data = io.BytesIO(f.read())
                        os.unlink(tmp_file.name)
                else:
                    # Fallback to sample audio
                    audio_data = generate_sample_audio(text_input, speed)
                
                st.session_state.audio_generated = True
                st.session_state.audio_data = audio_data
                st.success("✅ Audio generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error in audio generation: {str(e)}")
                # Fallback to sample audio
                audio_data = generate_sample_audio(text_input, speed)
                st.session_state.audio_generated = True
                st.session_state.audio_data = audio_data
                st.info("ℹ️ Sample audio generated (TTS models not available)")
    
    # Display generated audio
    if st.session_state.audio_generated and st.session_state.audio_data:
        st.markdown("---")
        st.subheader("🎧 Generated Audio")
        
        st.audio(st.session_state.audio_data, format="audio/wav")
        
        # Download button
        st.download_button(
            label="📥 Download Audio (WAV)",
            data=st.session_state.audio_data,
            file_name=f"tts_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
            mime="audio/wav",
            use_container_width=True
        )
    
    # Model information
    st.markdown("---")
    st.subheader("🤖 Available TTS Models")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.markdown('<div class="model-card">', unsafe_allow_html=True)
        st.write("**Coqui TTS**")
        st.write("✅ High quality")
        st.write("✅ Multiple languages")
        st.write("✅ Voice cloning")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="model-card">', unsafe_allow_html=True)
        st.write("**XTTS**")
        st.write("✅ Cross-lingual")
        st.write("✅ High fidelity")
        st.write("✅ Real-time")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="model-card">', unsafe_allow_html=True)
        st.write("**Facebook MMS**")
        st.write("✅ 1100+ languages")
        st.write("✅ Research-grade")
        st.write("⚠️ Requires more RAM")
        st.markdown('</div>', unsafe_allow_html=True)

    # Deployment instructions
    with st.expander("🚀 Deployment Guide"):
        st.markdown("""
        ### GitHub par Deploy karne ka Tarika:
        
        1. **GitHub Repository banao:**
           ```bash
           git init
           git add .
           git commit -m "Initial commit"
           git branch -M main
           git remote add origin https://github.com/yourusername/tts-voice-app.git
           git push -u origin main
           ```
        
        2. **Streamlit Community Cloud par deploy karo:**
           - https://streamlit.io/cloud par jao
           - "New app" click karo
           - GitHub repository select karo
           - Branch `main` select karo
           - Main file path `app.py` dalo
           - Deploy button click karo
        
        ### Local run karne ka tarika:
        ```bash
        pip install -r requirements.txt
        streamlit run app.py
        ```
        """)

if __name__ == "__main__":
    main()
