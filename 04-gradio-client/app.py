import requests, gradio as gr

def diagnose(message, history):
    r = requests.post(                                   # ACTION
        "http://127.0.0.1:8000/api/diagnose",            # ADDRESS
        json={"workflow": message }                     # PAYLOAD
    )
    return r.json()["plan"]

gr.ChatInterface(fn=diagnose).launch()