"""
Basic LLM Interaction Example
============================

This example demonstrates the fundamental patterns for interacting with LLMs using LiteLLM.
It shows both synchronous completion and asynchronous streaming responses.
"""

import asyncio
import json
from typing import Dict, Any, AsyncGenerator
import litellm
from litellm import completion, acompletion

# Configure LiteLLM
litellm.drop_params = True  # Drop unsupported params automatically
litellm.set_verbose = False  # Set to True for debugging


async def basic_completion() -> None:
    """Simple non-streaming completion example"""
    print("=== Basic Completion Example ===\n")
    
    # Simple completion
    response = completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage.dict()}")
    print()


async def streaming_completion() -> None:
    """Streaming completion example"""
    print("=== Streaming Completion Example ===\n")
    
    # Streaming response
    stream = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Count from 1 to 5 slowly."}
        ],
        stream=True
    )
    
    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    print(f"\n\nFull response: {full_response}")
    print()


async def multi_turn_conversation() -> None:
    """Multi-turn conversation example"""
    print("=== Multi-turn Conversation Example ===\n")
    
    messages = [
        {"role": "system", "content": "You are a helpful math tutor."}
    ]
    
    # Simulate a conversation
    user_inputs = [
        "What is 2 + 2?",
        "Now multiply that by 3",
        "What's the square root of that?"
    ]
    
    for user_input in user_inputs:
        print(f"User: {user_input}")
        messages.append({"role": "user", "content": user_input})
        
        response = await acompletion(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3
        )
        
        assistant_response = response.choices[0].message.content
        print(f"Assistant: {assistant_response}\n")
        
        messages.append({"role": "assistant", "content": assistant_response})


async def json_mode_example() -> None:
    """Example using JSON mode for structured output"""
    print("=== JSON Mode Example ===\n")
    
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract information and return as JSON."},
            {"role": "user", "content": "John is 25 years old and lives in New York. He works as a software engineer."}
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse the JSON response
    json_response = json.loads(response.choices[0].message.content)
    print("Extracted information:")
    print(json.dumps(json_response, indent=2))
    print()


async def error_handling_example() -> None:
    """Example showing proper error handling"""
    print("=== Error Handling Example ===\n")
    
    try:
        # This might fail if the model doesn't exist
        response = await acompletion(
            model="non-existent-model",
            messages=[{"role": "user", "content": "Hello"}]
        )
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Fallback to a different model
        print("\nFalling back to gpt-4o-mini...")
        response = await acompletion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}]
        )
        print(f"Fallback response: {response.choices[0].message.content}")


async def custom_system_prompt_example() -> None:
    """Example with custom system prompts for specific behaviors"""
    print("=== Custom System Prompt Example ===\n")
    
    system_prompts = {
        "concise": "You are a concise assistant. Answer in one sentence or less.",
        "verbose": "You are a verbose assistant. Provide detailed, comprehensive answers.",
        "emoji": "You are a fun assistant. Use emojis in every response! 🎉"
    }
    
    user_query = "What is Python?"
    
    for style, prompt in system_prompts.items():
        print(f"Style: {style}")
        response = await acompletion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7
        )
        print(f"Response: {response.choices[0].message.content}\n")


async def main():
    """Run all examples"""
    await basic_completion()
    await streaming_completion()
    await multi_turn_conversation()
    await json_mode_example()
    await error_handling_example()
    await custom_system_prompt_example()


if __name__ == "__main__":
    asyncio.run(main())