"""
Tests for the JARVIS Tool Contract and Registry (Phase 6).
"""

from dataclasses import dataclass

import pytest

from core.tools import (
    Tool,
    ToolAlreadyRegisteredError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistry,
    ToolResult,
    ToolValidationError,
)


@dataclass
class CalculatorInput:
    a: int
    b: int


def dummy_handler(text: str) -> str:
    return f"Echo: {text}"


def add_handler(a: int, b: int) -> int:
    return a + b


def result_handler() -> ToolResult:
    return ToolResult(success=True, data=42, message="Custom success")


def test_tool_validation_valid() -> None:
    """Test valid tool creation and metadata."""
    tool = Tool(
        name="test.echo",
        description="Echoes input text",
        handler=dummy_handler,
        metadata={"category": "utility", "risk": "L0"},
    )
    assert tool.name == "test.echo"
    assert tool.description == "Echoes input text"
    assert tool.metadata["category"] == "utility"
    assert tool.metadata["risk"] == "L0"


def test_tool_validation_invalid_name() -> None:
    """Test tool creation fails with invalid name format."""
    with pytest.raises(ToolValidationError):
        Tool(name="invalidname", description="Invalid name", handler=dummy_handler)

    with pytest.raises(ToolValidationError):
        Tool(name="system.", description="Trailing dot", handler=dummy_handler)

    with pytest.raises(ToolValidationError):
        Tool(name=".system", description="Leading dot", handler=dummy_handler)


def test_tool_validation_empty_description() -> None:
    """Test tool creation fails with empty or whitespace description."""
    with pytest.raises(ToolValidationError):
        Tool(name="system.test", description="", handler=dummy_handler)

    with pytest.raises(ToolValidationError):
        Tool(name="system.test", description="   ", handler=dummy_handler)


def test_tool_execution_success() -> None:
    """Test successful tool execution returning raw data wrapped in ToolResult."""
    tool = Tool(
        name="math.add",
        description="Adds two numbers",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    result = tool.execute({"a": 5, "b": 7})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.data == 12
    assert result.message == "Tool executed successfully."
    assert result.error is None


def test_tool_execution_custom_result() -> None:
    """Test tool execution returning a custom ToolResult directly."""
    tool = Tool(
        name="test.custom",
        description="Returns custom result",
        handler=result_handler,
    )
    result = tool.execute()
    assert result.success is True
    assert result.data == 42
    assert result.message == "Custom success"


def test_tool_input_validation_failure() -> None:
    """Test tool execution raises ToolValidationError on invalid input mapping."""
    tool = Tool(
        name="math.add",
        description="Adds two numbers",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    with pytest.raises(ToolValidationError):
        tool.execute({"a": 5})  # missing 'b'


def test_tool_execution_error() -> None:
    """Test tool execution raises ToolExecutionError when handler fails."""
    def failing_handler() -> None:
        raise RuntimeError("Internal boom")

    tool = Tool(
        name="test.fail",
        description="Fails execution",
        handler=failing_handler,
    )
    with pytest.raises(ToolExecutionError):
        tool.execute()


def test_registry_registration_and_lookup() -> None:
    """Test registering tools, retrieving them, and checking existence."""
    registry = ToolRegistry()
    t1 = Tool(name="system.status", description="Get system status", handler=dummy_handler)
    t2 = Tool(name="file.read", description="Read file contents", handler=dummy_handler)

    assert registry.has("system.status") is False

    registry.register(t1)
    registry.register(t2)

    assert registry.has("system.status") is True
    assert registry.get("system.status") is t1
    assert registry.get("file.read") is t2


def test_registry_duplicate_registration_raises_error() -> None:
    """Test duplicate tool registration raises ToolAlreadyRegisteredError."""
    registry = ToolRegistry()
    t1 = Tool(name="system.status", description="Status 1", handler=dummy_handler)
    t2 = Tool(name="system.status", description="Status 2", handler=dummy_handler)

    registry.register(t1)
    with pytest.raises(ToolAlreadyRegisteredError):
        registry.register(t2)


def test_registry_unknown_tool_raises_not_found() -> None:
    """Test looking up an unregistered tool raises ToolNotFoundError."""
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        registry.get("nonexistent.tool")


def test_registry_unregister() -> None:
    """Test unregistering a tool."""
    registry = ToolRegistry()
    t1 = Tool(name="system.status", description="Get system status", handler=dummy_handler)

    registry.register(t1)
    assert registry.has("system.status") is True

    registry.unregister("system.status")
    assert registry.has("system.status") is False
    with pytest.raises(ToolNotFoundError):
        registry.get("system.status")

    # Unregistering non-existent tool should be a safe no-op
    registry.unregister("nonexistent.tool")


def test_registry_list_tools_deterministic_order() -> None:
    """Test listing tools returns them sorted deterministically by name."""
    registry = ToolRegistry()
    t_z = Tool(name="z.tool", description="Z tool", handler=dummy_handler)
    t_a = Tool(name="a.tool", description="A tool", handler=dummy_handler)
    t_m = Tool(name="m.tool", description="M tool", handler=dummy_handler)

    registry.register(t_z)
    registry.register(t_a)
    registry.register(t_m)

    tools = registry.list_tools()
    assert len(tools) == 3
    assert tools[0].name == "a.tool"
    assert tools[1].name == "m.tool"
    assert tools[2].name == "z.tool"


def test_registry_clear() -> None:
    """Test clearing all tools from the registry."""
    registry = ToolRegistry()
    registry.register(Tool(name="a.tool", description="A", handler=dummy_handler))
    registry.register(Tool(name="b.tool", description="B", handler=dummy_handler))

    assert len(registry.list_tools()) == 2
    registry.clear()
    assert len(registry.list_tools()) == 0


def test_registry_isolation() -> None:
    """Test multiple ToolRegistry instances are fully isolated."""
    reg1 = ToolRegistry()
    reg2 = ToolRegistry()

    t = Tool(name="shared.name", description="Shared name", handler=dummy_handler)
    reg1.register(t)

    assert reg1.has("shared.name") is True
    assert reg2.has("shared.name") is False
