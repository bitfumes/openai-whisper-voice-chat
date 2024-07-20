from pathlib import Path

import streamlit as st
from audiorecorder import audiorecorder
from openai import OpenAI

open_ai = OpenAI(
    api_key="Your api secret")

st.set_page_config(
    layout="centered",
    page_icon="🤖",
    page_title="Voice Chat"
)

st.title("Voice Chat")

if 'chat' not in st.session_state:
    st.session_state.chat = []


def recordAudio():
    audio = audiorecorder("Click to record", "Click to stop recording")
    if len(audio) > 0:
        audio.export("audio.wav", format="wav")
        userPrompt = speechToText()
        st.text(userPrompt)
        st.session_state.chat.append({
            'role': 'user',
            'content': userPrompt
        })

        answer = getAnswer(userPrompt)
        st.session_state.chat.append({
            'role': 'assistant',
            'content': answer
        })
        textToSpeech(answer)
        st.audio("reply.wav", autoplay=True)


def speechToText():
    audio_file = open("audio.wav", "rb")
    transcription = open_ai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcription.text


def textToSpeech(text):
    speech_file_path = Path(__file__).parent / "reply.wav"
    response = open_ai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    response.stream_to_file(speech_file_path)


def getAnswer(question):
    response = open_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who provide very very short response"},
            *st.session_state.chat,
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content


recordAudio()
