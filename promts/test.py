import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import streamlit as st
from streamlit_chat import message
import logging
import uuid

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn(
        "Langflow provides a function to help you upload files to the flow. Please install langflow to use it."
    )
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "0815ea1d-2ab4-4062-8b04-0f1f624cc5ab"
ENDPOINT = ""  # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
    "Agent-Gw1p9": {},
    "ChatInput-ZWMni": {},
    "ChatOutput-DdhX4": {},
    "RedisChatMemory-aLnV7": {},
    "StoreMessage-ynUwv": {},
    "Memory-oWnSd": {},
    "Prompt-KUMOK": {},
    "SQLAgent-v5r6h": {},
    "CalculatorComponent-wTVM5": {},
    "GetEnvVar-wU1tK": {},
    "TavilySearchComponent-x6mKa": {},
    "GetEnvVar-T4ggR": {},
    "GetEnvVar-CGp2N": {},
    "OpenAIModel-LREKB": {},
    "Agent-W3z26": {},
    "Agent-IM8Jy": {},
    "Agent-6toAq": {},
}


def run_flow(
    message: str,
    session_id: str,
    endpoint: str,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = None,
    api_key: Optional[str] = None,
) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "session_id": session_id,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def main():
    st.set_page_config(page_title="PC build helper")

    st.markdown("##### Welcome to the PC build helper")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    session_id = st.session_state.session_id

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("I'm your PC build helper, how may I help you?"):
        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )
        # Display user message in chat message container
        with st.chat_message(
            "user",
        ):
            st.write(prompt)

        # Display assistant response in chat message container
        with st.chat_message(
            "assistant",
        ):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt, session_id=session_id)
                message_placeholder.write(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
            }
        )


def generate_response(prompt, session_id):
    logging.info(f"question: {prompt}")
    response = run_flow(
        message=prompt,
        session_id=session_id,
        endpoint=FLOW_ID,
        output_type="chat",
        input_type="chat",
        tweaks=TWEAKS,
        api_key="sk-HJywYjPk-Bl_hkCxwgPJEjXH3r_LE0WbhQJlob0VU_M",
    )
    try:
        # text_output = str(response)
        text_output = (
            response.get("outputs", [{}])[0]
            .get("outputs", [{}])[0]
            .get("results", {})
            .get("message", {})
            .get("text", "No response received.")
        )
        return text_output
    except Exception as e:
        logging.error(f"error: {e}")
        return "Sorry, there was a problem finding an answer for you."


if __name__ == "__main__":
    main()

