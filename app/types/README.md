# Types Module

This module contains TypedDict definitions to provide strong typing throughout the application and reduce the usage of `Dict[str, Any]` and `Any` types.

## Structure

- **`common.py`**: Common types used across the application
  - `ErrorDetails`: Standardized error detail structure
  - `MetadataDict`: Generic metadata dictionary with common fields

- **`agent.py`**: Agent-related type definitions
  - `AgentConfig`: Configuration for agent initialization
  - `Neo4jConfig`: Neo4j specific configuration
  - `VectorStoreConfig`: Vector store configuration
  - `AgentResponse`: Agent execution response
  - `AgentExecutionResult`: Complete agent execution result
  - `NodeReturnType`: Return type for agent workflow nodes

- **`guardrail.py`**: Guardrail validation types
  - `GuardrailValidationResult`: Result of guardrail validation
  - `GuardrailConfig`: Configuration for guardrail

- **`llm.py`**: LLM provider types
  - `LLMConfig`: Configuration for LLM
  - `LLMValidationResult`: Result of LLM input/output validation

- **`mcp.py`**: Model Context Protocol types
  - `MCPConfig`: Configuration for MCP client
  - `MCPExecuteParams`: Parameters for MCP execute command
  - `CypherExecutionResult`: Result of Cypher query execution
  - `Neo4jSchemaResult`: Neo4j schema information
  - `Neo4jValidationResult`: Result of Neo4j query validation
  - `Neo4jExplainResult`: Result of EXPLAIN query

- **`tool.py`**: Tool execution types
  - `ToolParams`: Parameters for tool execution
  - `ToolResult`: Result of tool execution
  - `ThinkToolResult`: Result from think tool
  - `PlanToolResult`: Result from plan tool

- **`vectorstore.py`**: Vector store types
  - `VectorStoreConfig`: Configuration for vector store
  - `VectorStoreFilter`: Filter for vector store queries
  - `VectorStoreStats`: Statistics about vector store
  - `DocumentWithScore`: Document with similarity score

## Usage

### Import from types module

```python
from app.types import AgentConfig, NodeReturnType
from app.types.guardrail import GuardrailValidationResult
from app.types.mcp import Neo4jValidationResult
```

### Using TypedDict for type safety

```python
def initialize_agent(config: AgentConfig) -> None:
    # TypedDict provides autocomplete and type checking
    llm_provider = config.get("llm_provider")
    temperature = config.get("temperature", 0.7)
    ...

def process_node(state: AgentState) -> NodeReturnType:
    # Return only the fields you need to update
    return {
        "response": "Generated response",
        "error": None
    }
```

### Benefits

1. **Type Safety**: Catch type errors at development time with type checkers
2. **IDE Support**: Better autocomplete and inline documentation
3. **Code Clarity**: Clear contracts for function inputs/outputs
4. **Maintainability**: Easier to refactor and update types
5. **Documentation**: Types serve as self-documenting code

## TypedDict Features

- **`total=False`**: Makes all fields optional (useful for partial updates)
- **Required fields**: Use `Required[Type]` annotation for mandatory fields
- **Inheritance**: TypedDict can extend other TypedDict classes

## Migration Guide

### Before
```python
def validate_query(query: str) -> Dict[str, Any]:
    return {
        "valid": True,
        "errors": [],
        "warnings": []
    }
```

### After
```python
def validate_query(query: str) -> Neo4jValidationResult:
    return {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestion": None
    }
```

## Best Practices

1. **Use specific types** instead of `Dict[str, Any]` whenever possible
2. **Create new TypedDict** for complex nested structures
3. **Set `total=False`** for partial state updates in nodes
4. **Document fields** with comments for clarity
5. **Keep types cohesive** - group related fields together

## Note

While we use TypedDict for better typing, Python's dynamic nature means these are runtime hints. Use a type checker like `mypy` or your IDE's built-in checker for full validation.
