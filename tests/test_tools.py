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


# -----------------------------------------------------------------------------
# Phase 6 Authority-Readiness Hardening Review
# -----------------------------------------------------------------------------


def test_tool_name_rejects_whitespace() -> None:
    """Tool names with whitespace must be rejected."""
    with pytest.raises(ToolValidationError):
        Tool(name="system get_status", description="Bad", handler=dummy_handler)


def test_tool_name_rejects_shell_like_syntax() -> None:
    """Tool names must not contain shell metacharacters."""
    with pytest.raises(ToolValidationError):
        Tool(name="system;rm", description="Bad", handler=dummy_handler)
    with pytest.raises(ToolValidationError):
        Tool(name="system|rm", description="Bad", handler=dummy_handler)
    with pytest.raises(ToolValidationError):
        Tool(name="system$rm", description="Bad", handler=dummy_handler)


def test_tool_name_rejects_uppercase() -> None:
    """Tool names must be lowercase (machine-readable convention)."""
    with pytest.raises(ToolValidationError):
        Tool(name="System.GetStatus", description="Bad", handler=dummy_handler)


def test_tool_name_accepts_nested_domain() -> None:
    """Tool names with multiple dot-separated segments are allowed."""
    t = Tool(name="system.status.get", description="Nested", handler=dummy_handler)
    assert t.name == "system.status.get"


def test_wrong_dataclass_type_rejected() -> None:
    """A tool expecting InputTypeA must not accept an arbitrary other dataclass."""
    @dataclass
    class OtherInput:
        x: str

    tool = Tool(
        name="math.add",
        description="Adds",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    with pytest.raises(ToolValidationError):
        tool.execute(OtherInput(x="nope"))


def test_non_dict_input_rejected_when_schema_present() -> None:
    """A non-dict, non-schema instance must be rejected when a schema is defined."""
    tool = Tool(
        name="math.add",
        description="Adds",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    with pytest.raises(ToolValidationError):
        tool.execute("not a dict")


def test_dict_input_accepted_when_schema_present() -> None:
    """A plain dict is still valid if it matches the dataclass schema."""
    tool = Tool(
        name="math.add",
        description="Adds",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    result = tool.execute({"a": 1, "b": 2})
    assert result.success is True
    assert result.data == 3


def test_missing_required_field_raises_validation_error() -> None:
    """Missing required fields must surface as ToolValidationError."""
    tool = Tool(
        name="math.add",
        description="Adds",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    with pytest.raises(ToolValidationError):
        tool.execute({"a": 1})


def test_extra_field_raises_validation_error() -> None:
    """Unexpected fields must surface as ToolValidationError."""
    tool = Tool(
        name="math.add",
        description="Adds",
        handler=add_handler,
        input_schema=CalculatorInput,
    )
    with pytest.raises(ToolValidationError):
        tool.execute({"a": 1, "b": 2, "c": 3})


def test_handler_returning_failure_result_not_raised() -> None:
    """A handler returning ToolResult(success=False) is NOT wrapped in an exception."""
    def soft_fail() -> ToolResult:
        return ToolResult(success=False, data=None, message="Expected failure")

    tool = Tool(name="test.softfail", description="Soft fail", handler=soft_fail)
    result = tool.execute()
    assert isinstance(result, ToolResult)
    assert result.success is False
    assert result.message == "Expected failure"


def test_tool_error_propagates_unchanged() -> None:
    """A handler raising ToolError must propagate without being re-wrapped."""
    def raise_tool_err() -> None:
        raise ToolValidationError("custom")

    tool = Tool(name="test.err", description="Err", handler=raise_tool_err)
    with pytest.raises(ToolValidationError, match="custom"):
        tool.execute()


def test_registry_does_not_expose_execute() -> None:
    """ToolRegistry must NOT have an execute method (authority bypass prevention)."""
    reg = ToolRegistry()
    assert not hasattr(reg, "execute"), (
        "ToolRegistry must not provide an execute() method; "
        "execution belongs to a controlled layer after Authority approval."
    )


def test_registry_get_returns_tool_not_authorization() -> None:
    """Getting a tool returns the Tool itself; it is not an authorization decision."""
    reg = ToolRegistry()
    t = Tool(name="system.test", description="Test", handler=dummy_handler)
    reg.register(t)
    retrieved = reg.get("system.test")
    assert retrieved is t
    # Calling execute on the retrieved Tool is the Tool's own contract, not the registry's.
    # This test only asserts the registry does not itself execute.
    assert not callable(getattr(reg, "execute", None))
