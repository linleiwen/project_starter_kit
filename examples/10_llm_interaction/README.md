# LLM Interaction Examples

This directory contains reusable examples for interacting with Large Language Models (LLMs) using LiteLLM. These examples are extracted and abstracted from the production chat service to provide clean, reusable patterns.

## Examples Overview

### 1. Basic LLM Interaction (`01_basic_llm_interaction.py`)
- Simple completion requests
- Streaming responses
- Multi-turn conversations
- JSON mode for structured output
- Error handling and fallback strategies
- Custom system prompts

### 2. LLM Performance Measurement (`02_llm_performance_measurement.py`)
- Response time tracking
- Token usage monitoring
- Cost estimation
- Performance statistics aggregation
- Batch performance testing
- Metrics export functionality

### 3. Tool Calling (`03_tool_calling.py`)
- Tool/function definition and registration
- Synchronous and asynchronous tool execution
- Multi-step tool calling chains
- Parallel tool execution
- Error handling for tool failures
- Tool result processing

### 4. Advanced Streaming with Tools (`04_streaming_with_tools.py`)
- Real-time streaming with function calling
- Event-based streaming architecture
- Concurrent streaming sessions
- Retry logic for unreliable tools
- Stream event tracking and analysis

### 5. Stateful Conversations (`05_stateful_conversation.py`)
- Using `aresponses` API for conversation continuity
- Session state management
- Context preservation across turns
- Parallel session handling
- Tool call history tracking

## Key Concepts

### LiteLLM Configuration
```python
import litellm
litellm.drop_params = True  # Drop unsupported params
litellm.set_verbose = False  # Disable verbose logging
```

### Performance Tracking Pattern
```python
tracker = LLMPerformanceTracker()
result = await tracker.track_completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
print(f"Duration: {result['metrics'].duration_ms}ms")
print(f"Cost: ${result['metrics'].estimated_cost}")
```

### Tool Registration Pattern
```python
handler = ToolHandler()
handler.register_tool(function_name, function_impl, schema)
```

### Stateful Conversation Pattern
```python
handler = StatefulConversationHandler()
result = await handler.process_message(
    session_id="unique_session_id",
    user_message="User input",
    system_prompt="System instructions"
)
```

## Running the Examples

Each example can be run independently:

```bash
python examples/10_llm_interaction/01_basic_llm_interaction.py
python examples/10_llm_interaction/02_llm_performance_measurement.py
# ... etc
```

## Integration Tips

1. **For Simple LLM Calls**: Use patterns from `01_basic_llm_interaction.py`
2. **For Production Monitoring**: Integrate `LLMPerformanceTracker` from `02_llm_performance_measurement.py`
3. **For Tool-Enabled Assistants**: Adapt patterns from `03_tool_calling.py`
4. **For Real-time Applications**: Use streaming patterns from `04_streaming_with_tools.py`
5. **For Chat Applications**: Build on `StatefulConversationHandler` from `05_stateful_conversation.py`

## Environment Setup

Ensure you have the required environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
# Or other LLM provider keys as needed
```

## Cost Considerations

The performance measurement example includes cost estimation. Current pricing (as of examples):
- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- GPT-4o: $5.00/1M input tokens, $15.00/1M output tokens
- GPT-3.5-turbo: $0.50/1M input tokens, $1.50/1M output tokens

Always verify current pricing with your LLM provider.