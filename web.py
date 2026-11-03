import streamlit as st
from chat import openai_client, agent_ref, agent, get_generated_files

st.title(agent.name)

if "conv" not in st.session_state:
    st.session_state.conv = openai_client.conversations.create().id
    st.session_state.history = []


def show(msg_id, role, text, files):
    with st.chat_message(role):
        st.write(text)
        for j, (name, data) in enumerate(files):
            st.download_button(
                f"Download {name}", data, file_name=name, key=f"dl-{msg_id}-{j}"
            )


for i, m in enumerate(st.session_state.history):
    show(i, m["role"], m["text"], m["files"])

if prompt := st.chat_input("Ask something about Microsoft technologies..."):
    n = len(st.session_state.history)
    show(n, "user", prompt, [])
    with st.spinner("Thinking..."):
        resp = openai_client.responses.create(
            conversation=st.session_state.conv,
            input=prompt,
            extra_body=agent_ref,
        )
        files = get_generated_files(resp)
    show(n + 1, "assistant", resp.output_text, files)
    st.session_state.history += [
        {"role": "user", "text": prompt, "files": []},
        {"role": "assistant", "text": resp.output_text, "files": files},
    ]