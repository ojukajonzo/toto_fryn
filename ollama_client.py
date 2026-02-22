"""
Ollama client wrapper using the official ollama Python package.
Communicates with local Ollama server via the ollama.chat() API.

This wrapper exposes `query_model(prompt, model)` which returns the model response string.
"""
import ollama
from typing import Optional


def query_model(prompt: str, model: str = "llama3.2:1b") -> str:
    """
    Query the Ollama model using ollama.chat() API.
    
    Args:
        prompt: The prompt/question to send to the model
        model: Name of the model to use (default: llama3.2:1b)
    
    Returns:
        The complete model response as a string
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama model '{model}' error: {e}")


def test_model(model: str = "llama3.2:1b") -> str:
    """
    Quick test to see if the model responds.
    Returns a brief response or raises an exception.
    """
    try:
        response = query_model("Respond with a single word: hello", model=model)
        return f"✓ Model '{model}' responded: {response[:100]}"
    except Exception as e:
        raise RuntimeError(f"✗ Model '{model}' failed: {e}")
