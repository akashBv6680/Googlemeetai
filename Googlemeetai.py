import streamlit as st
import whisper
import pyaudio
import wave
import requests
import os

# Load Together AI Key from Streamlit secrets
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Load Whisper Model
whisper_model = whisper.load_model("base")

st.set_page_config(page_title="Google Meet Agentic AI", layout="centered")
st.title("🎙️ Agentic AI for Google Meet Interview")

# Record audio from mic
def record_audio(filename="audio.wav", duration=6):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
    st.info("🎧 Listening... Speak now.")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return filename

# Transcribe audio using Whisper
def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path)
    return result["text"]

# Get response from Together AI
def generate_reply(question):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are answering live interview questions."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# Streamlit Button
if st.button("🎤 Record Question (6s)"):
    audio_file = record_audio()
    question = transcribe_audio(audio_file)
    st.subheader("❓ Recruiter Asked:")
    st.markdown(f"`{question}`")

    with st.spinner("🧠 Thinking..."):
        answer = generate_reply(question)

    st.subheader("💡 Agentic AI Answer:")
    st.success(answer)
