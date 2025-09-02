"""
OpenAI Helper Module

This module provides utilities for properly configuring OpenAI clients with API key validation.
Supports multiple providers including OpenAI, Gemini, and OpenRouter.
"""
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv


def get_client_config(model: str = None) -> dict:
    """
    Get client configuration based on the model provider.
    
    Args:
        model: Model name (e.g., "gemini/gemini-2.5-flash", "gpt-4")
        
    Returns:
        dict: Configuration for AsyncOpenAI client
        
    Raises:
        ValueError: If required API keys are not configured
    """
    load_dotenv()
    
    if model is None:
        model = get_model_name()
    
    # Gemini models configuration
    if model.startswith("gemini/"):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key in [
            "your_gemini_api_key_here", 
            "sua_chave_gemini_aqui", 
            "YOUR_GEMINI_API_KEY_HERE"
        ]:
            raise ValueError(
                "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable "
                "with a valid API key from https://aistudio.google.com/app/apikey"
            )
        
        return {
            "api_key": gemini_api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"
        }
    
    # OpenRouter models configuration
    elif model.startswith("openrouter/"):
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key or openrouter_api_key in [
            "your_openrouter_api_key_here", 
            "sua_chave_openrouter_aqui", 
            "YOUR_OPENROUTER_API_KEY_HERE"
        ]:
            raise ValueError(
                "OpenRouter API key is not configured. Please set the OPENROUTER_API_KEY environment variable "
                "with a valid API key from https://openrouter.ai/keys"
            )
        
        return {
            "api_key": openrouter_api_key,
            "base_url": "https://openrouter.ai/api/v1"
        }
    
    # Default OpenAI configuration
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Allow sk-1234 as a placeholder for Gemini setups
        if not openai_api_key or openai_api_key in [
            "your_openai_api_key_here", 
            "sua_chave_openai_aqui", 
            "YOUR_OPENAI_API_KEY_HERE"
        ]:
            raise ValueError(
                "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable "
                "with a valid API key from https://platform.openai.com/api-keys"
            )
        
        return {
            "api_key": openai_api_key
        }


def create_openai_client(model: str = None) -> AsyncOpenAI:
    """
    Create an AsyncOpenAI client with proper configuration for the specified model.
    
    Args:
        model: Model name to determine the correct provider configuration
        
    Returns:
        AsyncOpenAI: Configured OpenAI client
        
    Raises:
        ValueError: If API key is not configured or is a placeholder value
    """
    config = get_client_config(model)
    return AsyncOpenAI(**config)


def get_model_name() -> str:
    """
    Get the model name from environment variables with fallback.
    
    Returns:
        str: Model name to use
    """
    load_dotenv()
    return os.getenv("CAI_MODEL", "alias0")
