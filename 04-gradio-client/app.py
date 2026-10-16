import os

import gradio as gr
import requests

# Local server by default. For the live one: API_URL=https://<app>.vercel.app/api/diagnose
URL = os.environ.get("API_URL", "http://127.0.0.1:8000/api/diagnose")


def diagnose(workflow):
    return requests.post(URL, json={"workflow": workflow}).json()["plan"]


gr.Interface(diagnose, gr.Textbox(lines=8, label="Workflow"), gr.Textbox(label="Plan")).launch()
