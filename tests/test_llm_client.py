# tests/test_llm_client.py
from src.llm_client import Message, ToolDef


def test_message_dataclass():
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.tool_call_id is None


def test_tool_def_structure():
    def dummy_handler(**kwargs):
        return "ok"

    tool = ToolDef(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
        handler=dummy_handler
    )
    assert tool.name == "test_tool"
    assert tool.handler() == "ok"
