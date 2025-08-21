"""
Tool Calling Example
====================

This example demonstrates how to implement and use tools (function calling) with LLMs.
Shows tool definition, execution, and result handling patterns.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import litellm
from litellm import acompletion


class ToolHandler:
    """Base class for handling tool/function calls"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
    
    def register_tool(self, func: Callable, schema: Dict[str, Any]):
        """Register a tool with its schema"""
        name = schema["function"]["name"]
        self.tools[name] = func
        self.tool_schemas.append(schema)
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            func = self.tools[tool_name]
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                result = func(**arguments)
            
            return {"result": result}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}


# Example tool implementations
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in the specified timezone"""
    # Simplified for example - in production use pytz
    from datetime import datetime
    if timezone == "UTC":
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return datetime.now().strftime(f"%Y-%m-%d %H:%M:%S {timezone}")


def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression"""
    # Only allow safe operations
    allowed_chars = "0123456789+-*/(). "
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")
    
    try:
        result = eval(expression)
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


async def search_database(query: str, table: str = "products", limit: int = 5) -> List[Dict]:
    """Simulate database search"""
    # Simulate async database operation
    await asyncio.sleep(0.1)
    
    # Mock data
    mock_data = {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"id": 2, "name": "Phone", "price": 699.99, "category": "Electronics"},
            {"id": 3, "name": "Desk", "price": 299.99, "category": "Furniture"},
            {"id": 4, "name": "Chair", "price": 199.99, "category": "Furniture"},
            {"id": 5, "name": "Monitor", "price": 399.99, "category": "Electronics"},
        ],
        "users": [
            {"id": 1, "name": "Alice", "role": "Admin"},
            {"id": 2, "name": "Bob", "role": "User"},
            {"id": 3, "name": "Charlie", "role": "User"},
        ]
    }
    
    data = mock_data.get(table, [])
    
    # Simple search
    results = []
    for item in data:
        if query.lower() in str(item).lower():
            results.append(item)
            if len(results) >= limit:
                break
    
    return results


def create_weather_tool() -> Dict[str, Any]:
    """Create a weather tool schema"""
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units",
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        }
    }


async def get_weather(location: str, units: str = "celsius") -> Dict[str, Any]:
    """Mock weather API"""
    # Simulate API call
    await asyncio.sleep(0.2)
    
    # Mock weather data
    base_temp = 20
    if "new york" in location.lower():
        base_temp = 15
    elif "miami" in location.lower():
        base_temp = 28
    elif "london" in location.lower():
        base_temp = 12
    
    if units == "fahrenheit":
        base_temp = base_temp * 9/5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"
    
    return {
        "location": location,
        "temperature": f"{base_temp}{unit_symbol}",
        "conditions": "Partly cloudy",
        "humidity": "65%",
        "wind": "10 km/h"
    }


# Tool schemas
TIME_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current time in a specified timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone (e.g., UTC, EST, PST)",
                    "default": "UTC"
                }
            }
        }
    }
}

CALCULATOR_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
}

SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_database",
        "description": "Search for items in the database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "table": {
                    "type": "string",
                    "enum": ["products", "users"],
                    "description": "Table to search in",
                    "default": "products"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}


async def simple_tool_calling_example():
    """Basic example of tool calling"""
    print("=== Simple Tool Calling Example ===\n")
    
    # Create tool handler
    handler = ToolHandler()
    handler.register_tool(get_current_time, TIME_TOOL_SCHEMA)
    handler.register_tool(calculate, CALCULATOR_TOOL_SCHEMA)
    
    # Make request with tools
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What time is it in UTC and what is 42 * 17?"}
        ],
        tools=handler.tool_schemas,
        tool_choice="auto"
    )
    
    # Check for tool calls
    message = response.choices[0].message
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print(f"LLM wants to call {len(message.tool_calls)} tools\n")
        
        # Execute each tool call
        tool_results = []
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"Calling {func_name} with arguments: {arguments}")
            result = await handler.execute_tool(func_name, arguments)
            print(f"Result: {result}\n")
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        
        # Send tool results back to LLM
        follow_up = await acompletion(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "What time is it in UTC and what is 42 * 17?"},
                message.dict(),  # Include the assistant's response with tool calls
                {"role": "tool", "content": json.dumps(tool_results), "tool_call_id": "multi"}
            ]
        )
        
        print(f"Final response: {follow_up.choices[0].message.content}")
    else:
        print(f"Direct response: {message.content}")


async def multi_step_tool_calling():
    """Example with multiple rounds of tool calling"""
    print("\n=== Multi-Step Tool Calling Example ===\n")
    
    # Setup tools
    handler = ToolHandler()
    handler.register_tool(search_database, SEARCH_TOOL_SCHEMA)
    handler.register_tool(calculate, CALCULATOR_TOOL_SCHEMA)
    handler.register_tool(get_weather, create_weather_tool()["function"])
    
    # Add weather tool schema
    weather_schema = create_weather_tool()
    handler.tool_schemas.append(weather_schema)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to various tools."},
        {"role": "user", "content": "Find all electronics products, calculate their total price, and check the weather in New York."}
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"Iteration {iteration}:")
        
        # Get LLM response
        response = await acompletion(
            model="gpt-4o-mini",
            messages=messages,
            tools=handler.tool_schemas,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        messages.append(message.dict())
        
        # Check if LLM wants to use tools
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"LLM wants to call {len(message.tool_calls)} tool(s)")
            
            # Execute tools
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"  Calling {func_name} with {arguments}")
                result = await handler.execute_tool(func_name, arguments)
                
                # Add tool result to messages
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                }
                messages.append(tool_message)
                print(f"  Result: {result}")
            
            print()
        else:
            # No tool calls, print final response
            print(f"Final response: {message.content}\n")
            break


async def parallel_tool_execution():
    """Example showing parallel tool execution"""
    print("\n=== Parallel Tool Execution Example ===\n")
    
    handler = ToolHandler()
    handler.register_tool(get_weather, create_weather_tool()["function"])
    handler.register_tool(search_database, SEARCH_TOOL_SCHEMA)
    handler.register_tool(get_current_time, TIME_TOOL_SCHEMA)
    
    handler.tool_schemas.extend([
        create_weather_tool(),
        SEARCH_TOOL_SCHEMA,
        TIME_TOOL_SCHEMA
    ])
    
    # Request that requires multiple tools
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Get the weather in New York, Miami, and London. Also search for furniture products and tell me the current time."}
        ],
        tools=handler.tool_schemas,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print(f"LLM wants to call {len(message.tool_calls)} tools\n")
        
        # Execute all tools in parallel
        tasks = []
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"Scheduling {func_name} with {arguments}")
            task = handler.execute_tool(func_name, arguments)
            tasks.append((tool_call.id, func_name, task))
        
        print("\nExecuting all tools in parallel...")
        start_time = asyncio.get_event_loop().time()
        
        # Wait for all tasks to complete
        results = []
        for tool_id, func_name, task in tasks:
            result = await task
            results.append({
                "tool_call_id": tool_id,
                "function": func_name,
                "result": result
            })
        
        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"All tools completed in {elapsed:.2f} seconds\n")
        
        # Display results
        for r in results:
            print(f"{r['function']}: {r['result']}")


async def tool_error_handling():
    """Example showing tool error handling"""
    print("\n=== Tool Error Handling Example ===\n")
    
    handler = ToolHandler()
    handler.register_tool(calculate, CALCULATOR_TOOL_SCHEMA)
    
    # Request with invalid calculation
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Calculate this for me: 10 / 0"}
        ],
        tools=handler.tool_schemas,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"Calling {func_name} with {arguments}")
            result = await handler.execute_tool(func_name, arguments)
            print(f"Result: {result}")
            
            # Send error back to LLM
            follow_up = await acompletion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "Calculate this for me: 10 / 0"},
                    message.dict(),
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    }
                ]
            )
            
            print(f"LLM response to error: {follow_up.choices[0].message.content}")


async def main():
    """Run all tool calling examples"""
    await simple_tool_calling_example()
    await multi_step_tool_calling()
    await parallel_tool_execution()
    await tool_error_handling()


if __name__ == "__main__":
    asyncio.run(main())