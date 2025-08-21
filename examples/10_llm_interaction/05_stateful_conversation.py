"""
Stateful Conversation with aresponses Example
=============================================

This example demonstrates how to use LiteLLM's aresponses API for maintaining
stateful conversations across multiple interactions, similar to the chat_service.py implementation.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import litellm
from litellm import aresponses


class MessageRole(Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class ConversationState:
    """Maintain conversation state across interactions"""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_response_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls_history: List[Dict[str, Any]] = field(default_factory=list)


class StatefulConversationHandler:
    """Handler for stateful conversations using aresponses"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationState] = {}
        self.tools = {}
        self.tool_schemas = []
    
    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        """Register a tool for use in conversations"""
        self.tools[name] = func
        # Convert to aresponses format
        if "function" in schema:
            func_def = schema["function"]
            tool_schema = {
                "type": "function",
                "name": func_def.get("name"),
                "description": func_def.get("description"),
                "parameters": func_def.get("parameters", {})
            }
            self.tool_schemas.append(tool_schema)
    
    def get_or_create_session(self, session_id: str) -> ConversationState:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(session_id=session_id)
        return self.sessions[session_id]
    
    async def process_message(
        self,
        session_id: str,
        user_message: str,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """Process a user message in a stateful conversation"""
        
        session = self.get_or_create_session(session_id)
        
        # Add user message to history
        session.messages.append({
            "role": MessageRole.USER.value,
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Prepare for aresponses
        current_input = user_message
        current_response_id = session.last_response_id
        iteration = 0
        full_response = ""
        tool_calls_made = []
        
        print(f"\n[Session {session_id}] Processing message: {user_message}")
        
        while iteration < max_iterations:
            iteration += 1
            print(f"  Iteration {iteration}: ", end="")
            
            # Prepare aresponses kwargs
            kwargs = {
                "model": model,
                "tools": self.tool_schemas if self.tool_schemas else None,
                "input": current_input,
                "previous_response_id": current_response_id if current_response_id else None
            }
            
            # Add system prompt on first iteration of new session
            if iteration == 1 and len(session.messages) == 1 and system_prompt:
                kwargs["system"] = system_prompt
            
            try:
                # Call aresponses
                response = await aresponses(**kwargs)
                
                # Update response ID for continuity
                current_response_id = getattr(response, 'id', None)
                session.last_response_id = current_response_id
                
                # Parse response
                if hasattr(response, 'output') and isinstance(response.output, list):
                    # Check for tool calls
                    tool_calls = []
                    text_content = None
                    
                    for output_item in response.output:
                        # Check for tool calls
                        if hasattr(output_item, 'type'):
                            if output_item.type in ('tool_call', 'function_call'):
                                tool_calls.append(output_item)
                            elif output_item.type == 'message' and hasattr(output_item, 'tool_calls') and output_item.tool_calls:
                                tool_calls.extend(output_item.tool_calls)
                            elif output_item.type == 'message' and hasattr(output_item, 'content'):
                                # Extract text from message content
                                for content_item in output_item.content:
                                    if hasattr(content_item, 'type') and content_item.type == 'output_text' and hasattr(content_item, 'text'):
                                        text_content = content_item.text
                    
                    # Handle tool calls
                    if tool_calls:
                        print(f"executing {len(tool_calls)} tools")
                        tool_outputs = await self._execute_tools(tool_calls, session)
                        tool_calls_made.extend(tool_outputs)
                        
                        # Prepare tool outputs for next iteration
                        current_input = [
                            {
                                "type": "function_call_output",
                                "call_id": output["call_id"],
                                "output": json.dumps(output["result"], ensure_ascii=False)
                            }
                            for output in tool_outputs
                        ]
                        continue
                    
                    # Handle text response
                    if text_content:
                        print("got text response")
                        full_response = text_content
                        break
                
                # No tool calls or text, we're done
                print("no further actions")
                break
                
            except Exception as e:
                print(f"error: {e}")
                full_response = f"Error processing message: {str(e)}"
                break
        
        # Save assistant response to session
        session.messages.append({
            "role": MessageRole.ASSISTANT.value,
            "content": full_response,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls_made if tool_calls_made else None
        })
        
        return {
            "response": full_response,
            "session_id": session_id,
            "iterations": iteration,
            "tool_calls": len(tool_calls_made),
            "response_id": current_response_id
        }
    
    async def _execute_tools(self, tool_calls: List[Any], session: ConversationState) -> List[Dict[str, Any]]:
        """Execute tool calls and return results"""
        results = []
        
        for tc in tool_calls:
            # Extract tool details
            if hasattr(tc, 'type') and tc.type == 'function_call':
                name = getattr(tc, 'name', None)
                args_json = getattr(tc, 'arguments', '{}')
                call_id = getattr(tc, 'call_id', None)
            elif hasattr(tc, 'function'):
                func = tc.function
                name = getattr(func, 'name', None)
                args_json = getattr(func, 'arguments', '{}')
                call_id = getattr(tc, 'call_id', None) or getattr(tc, 'id', None)
            else:
                name = getattr(tc, 'name', None)
                args_json = getattr(tc, 'arguments', '{}')
                call_id = getattr(tc, 'call_id', None) or getattr(tc, 'id', None)
            
            if not name or name not in self.tools:
                results.append({
                    "call_id": call_id or f"error_{len(results)}",
                    "result": {"error": f"Unknown tool: {name}"}
                })
                continue
            
            # Execute tool
            try:
                args = json.loads(args_json) if args_json else {}
                func = self.tools[name]
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(**args)
                else:
                    result = func(**args)
                
                results.append({
                    "call_id": call_id or f"call_{name}_{len(results)}",
                    "tool": name,
                    "args": args,
                    "result": result,
                    "success": True
                })
                
                # Add to session history
                session.tool_calls_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "tool": name,
                    "args": args,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "call_id": call_id or f"error_{len(results)}",
                    "tool": name,
                    "result": {"error": str(e)},
                    "success": False
                })
        
        return results
    
    def get_session_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a session"""
        session = self.sessions.get(session_id)
        return session.messages if session else None
    
    def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Example tools
def get_user_info(user_id: str) -> Dict[str, Any]:
    """Get user information"""
    # Mock user database
    users = {
        "alice": {"name": "Alice Smith", "role": "Premium", "joined": "2023-01-15"},
        "bob": {"name": "Bob Johnson", "role": "Standard", "joined": "2023-06-20"},
        "charlie": {"name": "Charlie Brown", "role": "Premium", "joined": "2022-11-30"}
    }
    
    user = users.get(user_id.lower())
    if user:
        return {"found": True, "user": user}
    return {"found": False, "message": f"User {user_id} not found"}


async def check_account_balance(user_id: str, account_type: str = "checking") -> Dict[str, Any]:
    """Check account balance"""
    await asyncio.sleep(0.2)  # Simulate API call
    
    # Mock balances
    balances = {
        "alice": {"checking": 5420.50, "savings": 12000.00},
        "bob": {"checking": 1250.75, "savings": 3500.00},
        "charlie": {"checking": 8900.25, "savings": 25000.00}
    }
    
    user_balances = balances.get(user_id.lower(), {})
    balance = user_balances.get(account_type, 0)
    
    return {
        "user_id": user_id,
        "account_type": account_type,
        "balance": balance,
        "currency": "USD",
        "as_of": datetime.now().isoformat()
    }


# Tool schemas
USER_INFO_SCHEMA = {
    "function": {
        "name": "get_user_info",
        "description": "Get information about a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID to look up"
                }
            },
            "required": ["user_id"]
        }
    }
}

BALANCE_SCHEMA = {
    "function": {
        "name": "check_account_balance",
        "description": "Check account balance for a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID"
                },
                "account_type": {
                    "type": "string",
                    "enum": ["checking", "savings"],
                    "description": "Type of account",
                    "default": "checking"
                }
            },
            "required": ["user_id"]
        }
    }
}


async def demo_stateful_conversation():
    """Demonstrate stateful conversation with context preservation"""
    print("=== Stateful Conversation Demo ===")
    
    handler = StatefulConversationHandler()
    handler.register_tool("get_user_info", get_user_info, USER_INFO_SCHEMA)
    handler.register_tool("check_account_balance", check_account_balance, BALANCE_SCHEMA)
    
    session_id = "demo_session_001"
    system_prompt = """You are a helpful banking assistant. You have access to tools to:
- Look up user information
- Check account balances

Be concise and helpful. When users ask about their accounts, use the tools to get real information."""
    
    # Simulate a multi-turn conversation
    conversations = [
        "Hello, can you help me check my account?",
        "My user ID is alice",
        "What about my savings account?",
        "Can you also check Bob's checking account balance?"
    ]
    
    for i, message in enumerate(conversations):
        print(f"\nTurn {i+1}:")
        print(f"User: {message}")
        
        result = await handler.process_message(
            session_id=session_id,
            user_message=message,
            system_prompt=system_prompt
        )
        
        print(f"Assistant: {result['response']}")
        print(f"  (Iterations: {result['iterations']}, Tool calls: {result['tool_calls']})")
    
    # Show conversation history
    print("\n=== Conversation History ===")
    history = handler.get_session_history(session_id)
    for msg in history:
        role = msg['role']
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"[{role}]: {content}")
        if msg.get('tool_calls'):
            print(f"  Tool calls: {len(msg['tool_calls'])}")


async def demo_parallel_sessions():
    """Demonstrate handling multiple parallel sessions"""
    print("\n=== Parallel Sessions Demo ===")
    
    handler = StatefulConversationHandler()
    handler.register_tool("get_user_info", get_user_info, USER_INFO_SCHEMA)
    handler.register_tool("check_account_balance", check_account_balance, BALANCE_SCHEMA)
    
    # Create multiple sessions
    sessions = [
        ("session_001", "alice", "Check my checking account balance"),
        ("session_002", "bob", "What's my savings balance?"),
        ("session_003", "charlie", "Show me all my account balances")
    ]
    
    # Process all sessions in parallel
    tasks = []
    for session_id, user_id, message in sessions:
        # First establish user context
        await handler.process_message(
            session_id=session_id,
            user_message=f"My user ID is {user_id}",
            system_prompt="You are a banking assistant. Remember the user's ID for future queries."
        )
        
        # Then ask the actual question
        task = handler.process_message(
            session_id=session_id,
            user_message=message
        )
        tasks.append((session_id, task))
    
    # Wait for all to complete
    results = []
    for session_id, task in tasks:
        result = await task
        results.append((session_id, result))
    
    # Display results
    for session_id, result in results:
        print(f"\n{session_id}: {result['response']}")


async def demo_context_preservation():
    """Demonstrate context preservation across conversation turns"""
    print("\n=== Context Preservation Demo ===")
    
    handler = StatefulConversationHandler()
    
    # Custom tool that uses context
    async def remember_preference(preference: str, value: str) -> Dict[str, Any]:
        """Remember user preferences"""
        return {
            "saved": True,
            "preference": preference,
            "value": value
        }
    
    PREFERENCE_SCHEMA = {
        "function": {
            "name": "remember_preference",
            "description": "Remember a user preference",
            "parameters": {
                "type": "object",
                "properties": {
                    "preference": {"type": "string", "description": "Type of preference"},
                    "value": {"type": "string", "description": "Preference value"}
                },
                "required": ["preference", "value"]
            }
        }
    }
    
    handler.register_tool("remember_preference", remember_preference, PREFERENCE_SCHEMA)
    
    session_id = "context_demo"
    system_prompt = """You are a helpful assistant that remembers user preferences.
Use the remember_preference tool when users tell you their preferences.
Refer back to preferences you've saved in previous turns."""
    
    messages = [
        "I prefer to be called Dr. Smith",
        "My favorite color is blue",
        "Can you remind me what I told you earlier?"
    ]
    
    for msg in messages:
        print(f"\nUser: {msg}")
        result = await handler.process_message(
            session_id=session_id,
            user_message=msg,
            system_prompt=system_prompt
        )
        print(f"Assistant: {result['response']}")
    
    # Show tool call history
    session = handler.sessions[session_id]
    print("\n=== Tool Call History ===")
    for tc in session.tool_calls_history:
        print(f"Tool: {tc['tool']}, Args: {tc['args']}, Result: {tc['result']}")


async def main():
    """Run all stateful conversation examples"""
    await demo_stateful_conversation()
    await demo_parallel_sessions()
    await demo_context_preservation()


if __name__ == "__main__":
    asyncio.run(main())