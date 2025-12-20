import streamlit as st
import pandas as pd
import requests
import json

# --- Page Setup ---
st.set_page_config(layout="centered", page_title="Simple Widgets Demo")
st.title("Streamlit Widgets Showcase 🖼️")
st.subheader("Interactive Inputs and Outputs")


# 1. Text Input (Text Box)
latitude = st.text_input(
    "Enter your latitude:", 
    "12"
)

longitude = st.text_input(
    "Enter your longitude:", 
    "77"
)
st.write(f"Latitude, **{latitude}**,**{longitude}**!")

if st.button("GET DATA"):
    weather = requests.get(
    "https://api.open-meteo.com/v1/forecast?latitude="+latitude+"&longitude="+longitude+"&hourly=temperature_2m").json()


    prompt = f"Summarize this weather data: {weather['hourly']['temperature_2m'][:5]}"
    st.write("LLM Working")
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt},
        stream=True
    )
    res =""
    for line in resp.iter_lines():
        if line:
           res =res +" " +(json.loads(line.decode())["response"])
    st.write(res)

