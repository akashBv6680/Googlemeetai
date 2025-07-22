import streamlit as st
import whisper
import pyaudio
import wave
import requests
import os

# Load Together AI Key
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
whisper_model = whisper.load_model("base")

st.set_page_config(layout="centered")
st.title("🎙️ Agentic AI for Google Meet")

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

def transcribe_audio(file_path):
    result = whisper_model.transcribe(file_path)
    return result["text"]

def generate_reply(question):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are answering interview questions."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

if st.button("🎤 Record Question (6s)"):
    audio_file = record_audio()
    question = transcribe_audio(audio_file)
    st.subheader("❓ Recruiter Asked:")
    st.markdown(f"`{question}`")

    with st.spinner("Thinking..."):
        answer = generate_reply(question)

    st.subheader("💡 Suggested Answer:")
    st.success(answer)
