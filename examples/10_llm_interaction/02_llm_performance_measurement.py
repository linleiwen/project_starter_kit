"""
LLM Performance Measurement Example
===================================

This example demonstrates how to measure and monitor LLM performance metrics including:
- Response time tracking
- Token usage monitoring
- Cost estimation
- Performance statistics aggregation
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import litellm
from litellm import acompletion, completion


@dataclass
class LLMMetrics:
    """Container for LLM performance metrics"""
    model: str
    request_id: str
    start_time: float
    end_time: float
    duration_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    stream: bool
    status: str = "success"
    error: Optional[str] = None


class LLMPerformanceTracker:
    """Track and analyze LLM performance metrics"""
    
    def __init__(self):
        self.metrics: List[LLMMetrics] = []
        self.model_costs = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1K tokens
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            # Add more models as needed
        }
    
    def estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost based on token usage"""
        if model not in self.model_costs:
            return 0.0
        
        costs = self.model_costs[model]
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]
        return round(input_cost + output_cost, 6)
    
    async def track_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Track a single completion request"""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        try:
            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Extract usage information
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            # Calculate cost
            estimated_cost = self.estimate_cost(model, prompt_tokens, completion_tokens)
            
            # Create metrics
            metrics = LLMMetrics(
                model=model,
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
                stream=kwargs.get("stream", False)
            )
            
            self.metrics.append(metrics)
            
            return {
                "response": response,
                "metrics": metrics
            }
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Create error metrics
            metrics = LLMMetrics(
                model=model,
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost=0,
                stream=kwargs.get("stream", False),
                status="error",
                error=str(e)
            )
            
            self.metrics.append(metrics)
            raise
    
    async def track_streaming_completion(self, model: str, messages: List[Dict], **kwargs):
        """Track a streaming completion request"""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        # Force streaming
        kwargs["stream"] = True
        
        try:
            stream = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            
            # Collect chunks and track metrics
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)
                yield chunk
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Get final chunk with usage info
            if chunks and hasattr(chunks[-1], 'usage') and chunks[-1].usage:
                usage = chunks[-1].usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
            else:
                # Estimate if usage not available
                prompt_tokens = len(str(messages)) // 4  # Rough estimate
                completion_tokens = len(chunks) * 5  # Rough estimate
                total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            estimated_cost = self.estimate_cost(model, prompt_tokens, completion_tokens)
            
            # Create metrics
            metrics = LLMMetrics(
                model=model,
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
                stream=True
            )
            
            self.metrics.append(metrics)
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Create error metrics
            metrics = LLMMetrics(
                model=model,
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost=0,
                stream=True,
                status="error",
                error=str(e)
            )
            
            self.metrics.append(metrics)
            raise
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for all tracked requests"""
        if not self.metrics:
            return {}
        
        successful_metrics = [m for m in self.metrics if m.status == "success"]
        
        if not successful_metrics:
            return {
                "total_requests": len(self.metrics),
                "successful_requests": 0,
                "failed_requests": len(self.metrics),
                "error_rate": 1.0
            }
        
        total_duration = sum(m.duration_ms for m in successful_metrics)
        total_tokens = sum(m.total_tokens for m in successful_metrics)
        total_cost = sum(m.estimated_cost for m in successful_metrics)
        
        return {
            "total_requests": len(self.metrics),
            "successful_requests": len(successful_metrics),
            "failed_requests": len(self.metrics) - len(successful_metrics),
            "error_rate": (len(self.metrics) - len(successful_metrics)) / len(self.metrics),
            "avg_duration_ms": total_duration / len(successful_metrics),
            "min_duration_ms": min(m.duration_ms for m in successful_metrics),
            "max_duration_ms": max(m.duration_ms for m in successful_metrics),
            "total_tokens": total_tokens,
            "avg_tokens_per_request": total_tokens / len(successful_metrics),
            "total_estimated_cost": round(total_cost, 4),
            "avg_cost_per_request": round(total_cost / len(successful_metrics), 6),
            "by_model": self._get_model_stats()
        }
    
    def _get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics grouped by model"""
        model_stats = {}
        
        for metric in self.metrics:
            if metric.model not in model_stats:
                model_stats[metric.model] = {
                    "requests": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_duration_ms": 0,
                    "total_tokens": 0,
                    "total_cost": 0
                }
            
            stats = model_stats[metric.model]
            stats["requests"] += 1
            
            if metric.status == "success":
                stats["successful"] += 1
                stats["total_duration_ms"] += metric.duration_ms
                stats["total_tokens"] += metric.total_tokens
                stats["total_cost"] += metric.estimated_cost
            else:
                stats["failed"] += 1
        
        # Calculate averages
        for model, stats in model_stats.items():
            if stats["successful"] > 0:
                stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["successful"]
                stats["avg_tokens"] = stats["total_tokens"] / stats["successful"]
                stats["avg_cost"] = stats["total_cost"] / stats["successful"]
        
        return model_stats
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            "metrics": [asdict(m) for m in self.metrics],
            "summary": self.get_summary_stats(),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


async def demo_performance_tracking():
    """Demonstrate performance tracking with various scenarios"""
    tracker = LLMPerformanceTracker()
    
    print("=== LLM Performance Tracking Demo ===\n")
    
    # Test 1: Simple completion
    print("Test 1: Simple completion")
    result = await tracker.track_completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is 2+2?"}
        ],
        temperature=0
    )
    
    metrics = result["metrics"]
    print(f"Duration: {metrics.duration_ms:.2f}ms")
    print(f"Tokens: {metrics.total_tokens} (prompt: {metrics.prompt_tokens}, completion: {metrics.completion_tokens})")
    print(f"Estimated cost: ${metrics.estimated_cost:.6f}")
    print(f"Response: {result['response'].choices[0].message.content}\n")
    
    # Test 2: Longer completion
    print("Test 2: Longer completion")
    result = await tracker.track_completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in 3 paragraphs."}
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    metrics = result["metrics"]
    print(f"Duration: {metrics.duration_ms:.2f}ms")
    print(f"Tokens: {metrics.total_tokens}")
    print(f"Estimated cost: ${metrics.estimated_cost:.6f}\n")
    
    # Test 3: Streaming completion
    print("Test 3: Streaming completion")
    start = time.time()
    full_response = ""
    
    async for chunk in tracker.track_streaming_completion(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Count from 1 to 10"}
        ]
    ):
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    
    print(f"Streaming duration: {(time.time() - start) * 1000:.2f}ms")
    print(f"Response: {full_response}\n")
    
    # Test 4: Error handling
    print("Test 4: Error handling")
    try:
        await tracker.track_completion(
            model="non-existent-model",
            messages=[{"role": "user", "content": "Hello"}]
        )
    except Exception as e:
        print(f"Expected error: {e}\n")
    
    # Test 5: Multiple models comparison
    print("Test 5: Multiple models comparison")
    models = ["gpt-4o-mini", "gpt-3.5-turbo"]
    
    for model in models:
        try:
            result = await tracker.track_completion(
                model=model,
                messages=[
                    {"role": "user", "content": "What is the meaning of life?"}
                ],
                max_tokens=50
            )
            print(f"{model}: {result['metrics'].duration_ms:.2f}ms, ${result['metrics'].estimated_cost:.6f}")
        except Exception as e:
            print(f"{model}: Failed - {e}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    summary = tracker.get_summary_stats()
    print(json.dumps(summary, indent=2))
    
    # Export metrics
    tracker.export_metrics("llm_metrics_export.json")
    print("\nMetrics exported to llm_metrics_export.json")


async def demo_batch_performance():
    """Demonstrate performance tracking for batch operations"""
    tracker = LLMPerformanceTracker()
    
    print("\n=== Batch Performance Testing ===\n")
    
    questions = [
        "What is Python?",
        "Explain REST APIs",
        "What is machine learning?",
        "How does blockchain work?",
        "What is cloud computing?"
    ]
    
    # Concurrent requests
    print("Running concurrent requests...")
    tasks = []
    for q in questions:
        task = tracker.track_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": q}],
            max_tokens=50
        )
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = (time.time() - start_time) * 1000
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    print(f"Completed {successful}/{len(tasks)} requests in {total_time:.2f}ms")
    print(f"Average time per request: {total_time/len(tasks):.2f}ms")
    
    # Show final statistics
    stats = tracker.get_summary_stats()
    print(f"Total tokens used: {stats['total_tokens']}")
    print(f"Total estimated cost: ${stats['total_estimated_cost']:.4f}")


if __name__ == "__main__":
    asyncio.run(demo_performance_tracking())
    asyncio.run(demo_batch_performance())