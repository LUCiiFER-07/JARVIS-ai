"""
Tool Contract and Registry for JARVIS (Phase 6).

Provides the foundational architecture for tool definition, input validation,
structured results, exceptions, and deterministic tool registration and lookup.

Tool Execution Contract:
- Input validation errors (contract violations) raise ToolValidationError.
- Unexpected internal handler errors (programmer/contract failures) raise ToolExecutionError.
- Normal tool-operation failures (e.g., file not found, API error) return ToolResult(success=False).
"""

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)

# Valid tool name pattern: domain.action (e.g., system.get_status, file.read)
TOOL_NAME_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")


class ToolError(Exception):
    """Base exception for all tool-related errors."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool does not exist in the registry."""


class ToolAlreadyRegisteredError(ToolError):
    """Raised when attempting to register a tool with an already-used name."""


class ToolValidationError(ToolError):
    """Raised when tool input validation fails (contract violation)."""


class ToolExecutionError(ToolError):
    """Raised when tool execution encounters an unexpected internal error (programmer/contract failure)."""


@dataclass(frozen=True)
class ToolResult:
    """
    Structured result contract returned by tool execution.

    NOTE on immutability: frozen=True only prevents attribute reassignment.
    Mutable objects within the 'data' field (e.g., dicts, lists) are NOT deeply frozen.
    """

    success: bool
    data: Any = None
    message: str = ""
    error: str | None = None


@dataclass
class Tool:
    """
    Represents a registered tool capability in JARVIS.

    Registration in ToolRegistry means "this capability exists."
    It does NOT imply "this capability is permitted." (Phase 7 Authority handles permissions).
    """

    name: str
    description: str
    handler: Callable[..., Any]
    input_schema: Any | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not TOOL_NAME_PATTERN.match(self.name):
            raise ToolValidationError(
                f"Invalid tool name '{self.name}'. Must follow domain.action format (lowercase alphanumeric and dots)."
            )
        if not self.description or not self.description.strip():
            raise ToolValidationError(f"Tool '{self.name}' must have a non-empty description.")

    def validate_input(self, input_data: dict[str, Any]) -> Any:
        """
        Validate input_data against input_schema if defined.

        Phase 6 Validation Guarantees:
        - If input_schema is a dataclass, input_data must be a dict that can successfully instantiate it.
        - If input_data is already an instance of the schema, it is returned as-is.
        - Arbitrary dicts are NOT blindly accepted if a schema is defined.
        - Does NOT validate individual primitive field types beyond what the dataclass constructor enforces.
        """
        if self.input_schema is None:
            return input_data

        # If input_schema is a dataclass
        if isinstance(self.input_schema, type) and hasattr(self.input_schema, "__dataclass_fields__"):
            try:
                if isinstance(input_data, self.input_schema):
                    return input_data
                if not isinstance(input_data, dict):
                    raise ToolValidationError(
                        f"Invalid input type for tool '{self.name}': Expected dict, got {type(input_data).__name__}."
                    )
                return self.input_schema(**input_data)
            except TypeError as e:
                raise ToolValidationError(f"Invalid input for tool '{self.name}': {e}") from e

        return input_data

    def execute(self, input_data: dict[str, Any] | Any = None) -> ToolResult:
        """
        Validate input and execute tool handler, returning a structured ToolResult.

        Semantic distinction:
        - ToolValidationError: Bad input / contract violation (programmer or caller error).
        - ToolExecutionError: Unexpected internal failure (programmer error / infrastructure issue).
        - ToolResult(success=False): Normal tool-operation failure (expected runtime condition).
        """
        data = input_data if input_data is not None else {}
        try:
            validated_input = self.validate_input(data)
            if isinstance(validated_input, dict):
                result = self.handler(**validated_input)
            elif hasattr(validated_input, "__dataclass_fields__"):
                result = self.handler(**asdict(validated_input))
            else:
                result = self.handler(validated_input)

            if isinstance(result, ToolResult):
                return result
            return ToolResult(success=True, data=result, message="Tool executed successfully.")
        except ToolError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"Error executing tool '{self.name}': {e}") from e


class ToolRegistry:
    """
    Central registry for JARVIS tools. Manages deterministic tool registration,
    lookup, unregistration, and listing.

    SECURITY INVARIANT:
    ToolRegistry is NOT a security boundary. Registration means capability exists,
    not that it is permitted. Phase 7 Authority Engine will handle permission decisions.

    Registry does NOT execute tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool. Raises ToolAlreadyRegisteredError if name is already registered.
        """
        if not isinstance(tool, Tool):
            raise ToolValidationError("Only Tool instances can be registered.")
        if tool.name in self._tools:
            raise ToolAlreadyRegisteredError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    def unregister(self, name: str) -> None:
        """
        Unregister a tool by name. Silently ignores if not found.
        """
        if name in self._tools:
            del self._tools[name]
            logger.info("Unregistered tool: %s", name)

    def get(self, name: str) -> Tool:
        """
        Retrieve a tool by name. Raises ToolNotFoundError if not found.
        """
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def has(self, name: str) -> bool:
        """
        Check if a tool is registered.
        """
        return name in self._tools

    def list_tools(self) -> list[Tool]:
        """
        List all registered tools, sorted deterministically by name.
        """
        return [self._tools[name] for name in sorted(self._tools.keys())]

    def clear(self) -> None:
        """
        Clear all registered tools (primarily for testing).
        """
        self._tools.clear()
        logger.info("Cleared tool registry.")
