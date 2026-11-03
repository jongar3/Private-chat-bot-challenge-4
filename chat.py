import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient

PROJECT_ENDPOINT = os.getenv(
    "PROJECT_ENDPOINT",
    "https://foundry-tecnun-resource.services.ai.azure.com/api/projects/foundry-tecnun-project",
)
AGENT_NAME = os.getenv("AGENT_NAME", "AgenteLAB")
DOWNLOAD_DIR = "downloads"


def get_credential():
    """Try the Azure CLI / env credentials first, fall back to a browser login."""
    try:
        cred = DefaultAzureCredential()
        cred.get_token("https://ai.azure.com/.default")
        return cred
    except Exception:
        return InteractiveBrowserCredential()


project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=get_credential())
openai_client = project_client.get_openai_client()
agent = project_client.agents.get(agent_name=AGENT_NAME)
agent_ref = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}


def ask(conversation_id: str, user_input) -> object:
    return openai_client.responses.create(
        conversation=conversation_id,
        input=user_input,
        extra_body=agent_ref,
    )


def get_generated_files(response) -> list[tuple[str, bytes]]:
    """Download files created by Code Interpreter. Returns [(filename, bytes), ...]."""
    files, seen = [], set()
    for item in response.output:
        if item.type != "message":
            continue
        for block in item.content:
            for ann in getattr(block, "annotations", None) or []:
                if ann.type == "container_file_citation" and ann.file_id not in seen:
                    seen.add(ann.file_id)
                    content = openai_client.containers.files.content.retrieve(
                        file_id=ann.file_id,
                        container_id=ann.container_id,
                    )
                    name = os.path.basename(ann.filename or f"{ann.file_id}.bin")
                    files.append((name, content.read()))
    return files


def save_files(files: list[tuple[str, bytes]]) -> list[str]:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    paths = []
    for name, data in files:
        path = os.path.join(DOWNLOAD_DIR, name)
        with open(path, "wb") as f:
            f.write(data)
        paths.append(os.path.abspath(path))
    return paths


def resolve_approvals(conversation_id: str, response):
    """Loop while the MCP server asks for permission to call a tool."""
    while True:
        approvals = [i for i in response.output if i.type == "mcp_approval_request"]
        if not approvals:
            return response
        decisions = []
        for req in approvals:
            print(f"\n[MCP] {req.server_label} wants to call '{req.name}'")
            ok = input("Approve? [Y/n] ").strip().lower() != "n"
            decisions.append(
                {
                    "type": "mcp_approval_response",
                    "approval_request_id": req.id,
                    "approve": ok,
                }
            )
        response = ask(conversation_id, decisions)


def run_turn(conversation_id: str, prompt: str):
    response = resolve_approvals(conversation_id, ask(conversation_id, prompt))

    for item in response.output:
        if item.type == "mcp_call":
            print(f"  [tool] MCP -> {item.name}")
        elif item.type == "code_interpreter_call":
            print("  [tool] Code Interpreter")
        elif item.type == "file_search_call":
            print("  [tool] Knowledge search (your PDFs)")

    print(f"\nAgent: {response.output_text}\n")

    for path in save_files(get_generated_files(response)):
        print(f"  [file saved] {path}")
    print()


def main():
    print(f"Connected to agent: {agent.name}")
    conversation = openai_client.conversations.create()
    print("Type 'exit' to quit.\n")

    while True:
        prompt = input("You: ").strip()
        if prompt.lower() in {"exit", "quit"}:
            break
        if not prompt:
            continue
        try:
            run_turn(conversation.id, prompt)
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()