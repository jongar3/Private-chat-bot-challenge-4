# web.py
import streamlit as st
from chat import openai_client, agent_ref, agent  # reuses the connection above

st.title(f"{agent.name}")

if "conv" not in st.session_state:
    st.session_state.conv = openai_client.conversations.create().id
    st.session_state.history = []

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

if prompt := st.chat_input("Ask something about Microsoft technologies..."):
    st.chat_message("user").write(prompt)
    with st.spinner("Thinking..."):
        resp = openai_client.responses.create(
            conversation=st.session_state.conv,
            input=prompt,
            extra_body=agent_ref,
        )
    print(f"Agent: {resp.output_text}\n")
    st.chat_message("assistant").write(resp.output_text)
    st.session_state.history += [("user", prompt), ("assistant", resp.output_text)]