"""
Advanced Streaming with Tools Example
=====================================

This example demonstrates advanced patterns for streaming responses while handling tool calls.
Shows how to implement real-time streaming with function calling capabilities.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, AsyncGenerator, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import litellm
from litellm import acompletion


class StreamEventType(Enum):
    """Types of events during streaming"""
    TEXT = "text"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_ARGS = "tool_call_args"
    TOOL_CALL_END = "tool_call_end"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    END = "end"


@dataclass
class StreamEvent:
    """Event emitted during streaming"""
    type: StreamEventType
    data: Any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class StreamingToolHandler:
    """Advanced handler for streaming with tools"""
    
    def __init__(self):
        self.tools = {}
        self.tool_schemas = []
        self.current_tool_calls = {}  # Track ongoing tool calls
    
    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        """Register a tool"""
        self.tools[name] = func
        self.tool_schemas.append(schema)
    
    async def stream_with_tools(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        **kwargs
    ) -> AsyncGenerator[StreamEvent, None]:
        """Stream response with tool handling"""
        
        # Add tools to kwargs
        kwargs['tools'] = self.tool_schemas
        kwargs['tool_choice'] = kwargs.get('tool_choice', 'auto')
        kwargs['stream'] = True
        
        try:
            # Get streaming response
            stream = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            
            # Process stream chunks
            async for chunk in stream:
                # Process chunk and yield events
                async for event in self._process_chunk(chunk):
                    yield event
            
            # Handle any pending tool calls
            if self.current_tool_calls:
                async for event in self._execute_pending_tools():
                    yield event
            
            yield StreamEvent(StreamEventType.END, None)
            
        except Exception as e:
            yield StreamEvent(StreamEventType.ERROR, str(e))
    
    async def _process_chunk(self, chunk) -> AsyncGenerator[StreamEvent, None]:
        """Process a single chunk from the stream"""
        choice = chunk.choices[0] if chunk.choices else None
        if not choice:
            return
        
        # Check for text content
        if hasattr(choice.delta, 'content') and choice.delta.content:
            yield StreamEvent(
                StreamEventType.TEXT,
                choice.delta.content
            )
        
        # Check for tool calls
        if hasattr(choice.delta, 'tool_calls') and choice.delta.tool_calls:
            for tool_call_delta in choice.delta.tool_calls:
                await self._process_tool_call_delta(tool_call_delta)
                
                # Yield events for tool call progress
                if hasattr(tool_call_delta, 'function'):
                    if hasattr(tool_call_delta.function, 'name') and tool_call_delta.function.name:
                        yield StreamEvent(
                            StreamEventType.TOOL_CALL_START,
                            {
                                "id": tool_call_delta.id,
                                "name": tool_call_delta.function.name
                            }
                        )
                    
                    if hasattr(tool_call_delta.function, 'arguments') and tool_call_delta.function.arguments:
                        yield StreamEvent(
                            StreamEventType.TOOL_CALL_ARGS,
                            {
                                "id": tool_call_delta.id,
                                "arguments_chunk": tool_call_delta.function.arguments
                            }
                        )
    
    async def _process_tool_call_delta(self, tool_call_delta):
        """Process tool call delta from streaming"""
        tool_id = tool_call_delta.id if hasattr(tool_call_delta, 'id') else None
        if not tool_id:
            return
        
        # Initialize tool call tracking
        if tool_id not in self.current_tool_calls:
            self.current_tool_calls[tool_id] = {
                "id": tool_id,
                "name": "",
                "arguments": ""
            }
        
        # Update tool call information
        if hasattr(tool_call_delta, 'function'):
            func = tool_call_delta.function
            if hasattr(func, 'name') and func.name:
                self.current_tool_calls[tool_id]["name"] = func.name
            if hasattr(func, 'arguments') and func.arguments:
                self.current_tool_calls[tool_id]["arguments"] += func.arguments
    
    async def _execute_pending_tools(self) -> AsyncGenerator[StreamEvent, None]:
        """Execute all pending tool calls"""
        for tool_id, tool_info in self.current_tool_calls.items():
            # Emit tool call end event
            yield StreamEvent(
                StreamEventType.TOOL_CALL_END,
                {
                    "id": tool_id,
                    "name": tool_info["name"],
                    "arguments": tool_info["arguments"]
                }
            )
            
            # Execute tool
            tool_name = tool_info["name"]
            if tool_name in self.tools:
                try:
                    args = json.loads(tool_info["arguments"])
                    func = self.tools[tool_name]
                    
                    # Execute tool (handle both sync and async)
                    if asyncio.iscoroutinefunction(func):
                        result = await func(**args)
                    else:
                        result = func(**args)
                    
                    yield StreamEvent(
                        StreamEventType.TOOL_RESULT,
                        {
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "result": result,
                            "success": True
                        }
                    )
                except Exception as e:
                    yield StreamEvent(
                        StreamEventType.TOOL_RESULT,
                        {
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "error": str(e),
                            "success": False
                        }
                    )
        
        # Clear pending tools
        self.current_tool_calls.clear()


# Example tools for demonstration
async def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Simulate getting stock price"""
    await asyncio.sleep(0.5)  # Simulate API delay
    
    # Mock prices
    prices = {
        "AAPL": 185.52,
        "GOOGL": 142.83,
        "MSFT": 378.91,
        "AMZN": 172.35
    }
    
    price = prices.get(symbol.upper(), 100.00)
    return {
        "symbol": symbol.upper(),
        "price": price,
        "currency": "USD",
        "timestamp": time.time()
    }


async def get_news_headlines(category: str = "tech", limit: int = 3) -> List[str]:
    """Simulate getting news headlines"""
    await asyncio.sleep(0.3)
    
    headlines = {
        "tech": [
            "AI breakthrough: New model achieves human-level reasoning",
            "Tech giant announces quantum computing milestone",
            "Cybersecurity alert: Major vulnerability discovered"
        ],
        "business": [
            "Markets rally on positive economic data",
            "Major merger announced in retail sector",
            "Central bank hints at policy changes"
        ],
        "science": [
            "Scientists discover new exoplanet in habitable zone",
            "Breakthrough in cancer research shows promise",
            "Climate study reveals accelerating changes"
        ]
    }
    
    return headlines.get(category, ["No headlines available"])[:limit]


# Tool schemas
STOCK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Get current stock price for a symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., AAPL, GOOGL)"
                }
            },
            "required": ["symbol"]
        }
    }
}

NEWS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_news_headlines",
        "description": "Get latest news headlines",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["tech", "business", "science"],
                    "description": "News category",
                    "default": "tech"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of headlines",
                    "default": 3
                }
            }
        }
    }
}


async def demo_streaming_with_tools():
    """Demonstrate streaming with tool calls"""
    print("=== Streaming with Tools Demo ===\n")
    
    handler = StreamingToolHandler()
    handler.register_tool("get_stock_price", get_stock_price, STOCK_TOOL_SCHEMA)
    handler.register_tool("get_news_headlines", get_news_headlines, NEWS_TOOL_SCHEMA)
    
    messages = [
        {"role": "user", "content": "What's the current price of AAPL and MSFT stocks? Also get me the latest tech news."}
    ]
    
    print("User: " + messages[0]["content"] + "\n")
    print("Assistant: ", end="", flush=True)
    
    # Track events for analysis
    events_log = []
    full_response = ""
    
    async for event in handler.stream_with_tools("gpt-4o-mini", messages):
        events_log.append(event)
        
        if event.type == StreamEventType.TEXT:
            print(event.data, end="", flush=True)
            full_response += event.data
        
        elif event.type == StreamEventType.TOOL_CALL_START:
            print(f"\n[Starting tool call: {event.data['name']}]", end="", flush=True)
        
        elif event.type == StreamEventType.TOOL_RESULT:
            if event.data['success']:
                print(f"\n[Tool {event.data['tool_name']} completed]", end="", flush=True)
            else:
                print(f"\n[Tool {event.data['tool_name']} failed: {event.data['error']}]", end="", flush=True)
    
    print("\n")
    
    # Show event summary
    print("\n=== Event Summary ===")
    event_counts = {}
    for event in events_log:
        event_counts[event.type.value] = event_counts.get(event.type.value, 0) + 1
    
    for event_type, count in event_counts.items():
        print(f"{event_type}: {count}")


async def demo_concurrent_streaming():
    """Demonstrate handling multiple concurrent streaming sessions"""
    print("\n=== Concurrent Streaming Demo ===\n")
    
    async def process_user_query(user_id: int, query: str, handler: StreamingToolHandler):
        """Process a single user query"""
        print(f"[User {user_id}] Query: {query}")
        
        messages = [{"role": "user", "content": query}]
        response_parts = []
        
        async for event in handler.stream_with_tools("gpt-4o-mini", messages):
            if event.type == StreamEventType.TEXT:
                response_parts.append(event.data)
            elif event.type == StreamEventType.END:
                break
        
        full_response = "".join(response_parts)
        print(f"[User {user_id}] Response: {full_response[:100]}...")
        return user_id, full_response
    
    # Create multiple handlers for concurrent sessions
    queries = [
        (1, "What's the price of AAPL?"),
        (2, "Get me business news headlines"),
        (3, "What's the price of GOOGL and latest tech news?")
    ]
    
    tasks = []
    for user_id, query in queries:
        handler = StreamingToolHandler()
        handler.register_tool("get_stock_price", get_stock_price, STOCK_TOOL_SCHEMA)
        handler.register_tool("get_news_headlines", get_news_headlines, NEWS_TOOL_SCHEMA)
        
        task = process_user_query(user_id, query, handler)
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    print(f"\nProcessed {len(results)} queries in {elapsed:.2f} seconds")


async def demo_streaming_with_retry():
    """Demonstrate streaming with retry logic for failed tools"""
    print("\n=== Streaming with Retry Demo ===\n")
    
    # Tool that sometimes fails
    async def unreliable_api(query: str) -> str:
        import random
        if random.random() < 0.5:
            raise Exception("API temporarily unavailable")
        return f"Result for: {query}"
    
    # Wrapper with retry logic
    async def reliable_api(query: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                return await unreliable_api(query)
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Failed after {max_retries} attempts: {str(e)}"
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
    
    API_TOOL_SCHEMA = {
        "type": "function",
        "function": {
            "name": "reliable_api",
            "description": "Query an API with retry logic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query string"}
                },
                "required": ["query"]
            }
        }
    }
    
    handler = StreamingToolHandler()
    handler.register_tool("reliable_api", reliable_api, API_TOOL_SCHEMA)
    
    messages = [
        {"role": "user", "content": "Query the API with 'test data' please"}
    ]
    
    print("Streaming response with retry-enabled tool:\n")
    
    async for event in handler.stream_with_tools("gpt-4o-mini", messages):
        if event.type == StreamEventType.TEXT:
            print(event.data, end="", flush=True)
        elif event.type == StreamEventType.TOOL_RESULT:
            print(f"\n[Tool result: {event.data}]")


async def main():
    """Run all streaming examples"""
    await demo_streaming_with_tools()
    await demo_concurrent_streaming()
    await demo_streaming_with_retry()


if __name__ == "__main__":
    asyncio.run(main())