import gradio as gr
import requests

URL = "https://YOUR-APP.vercel.app/api/diagnose"


def diagnose(workflow):
    return requests.post(URL, json={"workflow": workflow}).json()["plan"]


gr.Interface(diagnose, gr.Textbox(lines=8, label="Workflow"), gr.Textbox(label="Plan")).launch()
