import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load API Key
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Agentic AI for replies
def generate_reply(question):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You're helping answer job interview questions."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# === Streamlit UI ===
st.set_page_config(page_title="Agentic AI for Meet", layout="centered")
st.title("🎤 Google Meet Agentic AI Assistant")

meet_url = st.text_input("🔗 Paste Google Meet Link Here")

if st.button("🚀 Start Listening"):
    st.info("Launching headless browser to read captions...")

    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()), options=chrome_options)
    driver.get(meet_url)

    st.warning("⚠️ Login manually if prompted. Turn on captions in Meet.")

    last_text = ""
    placeholder_q = st.empty()
    placeholder_a = st.empty()

    try:
        while True:
            # Locate captions (Meet uses a span for each word)
            spans = driver.find_elements(By.CSS_SELECTOR, 'div[jsname="GZx4me"] span')
            transcript = " ".join([s.text for s in spans])

            if transcript.strip() and transcript.strip() != last_text:
                last_text = transcript.strip()
                placeholder_q.markdown(f"**❓ Recruiter Asked:** `{transcript}`")

                with st.spinner("💡 Thinking..."):
                    answer = generate_reply(transcript)
                placeholder_a.success(answer)

            time.sleep(5)

    except Exception as e:
        st.error(f"🛑 Error: {e}")
        driver.quit()
