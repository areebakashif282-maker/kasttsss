# 🎤 AI Text-to-Speech with Voice Cloning

A powerful Streamlit web application that provides best AI TTS models with instant voice cloning capabilities.

## 🌟 Features

- **Multiple TTS Models**: Coqui TTS, XTTS, Facebook MMS, Tortoise TTS
- **Voice Cloning**: Upload reference audio for instant voice cloning
- **Multi-language Support**: English, Hindi, Spanish, French, German, Chinese, Japanese
- **Real-time Generation**: Instant audio generation
- **Download Capability**: Download generated audio files

## 🚀 Quick Deployment

### Method 1: Streamlit Community Cloud (Easiest)

1. Fork this repository
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your forked repository
5. Set main file path to `app.py`
6. Click "Deploy"

### Method 2: Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/tts-voice-app.git
cd tts-voice-app

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
