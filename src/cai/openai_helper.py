# OpenAI Helper module - compatibility layer
# Re-exports functions from main util module to maintain backward compatibility

from cai.util import (
    create_openai_client,
    get_client_config
)
import os

def get_model_name(model=None):
    """Get the current model name from environment."""
    if model is not None:
        return model
    return os.getenv('CAI_MODEL', 'openrouter/mistralai/mistral-small-3.2-24b-instruct:free')

def get_model_name_openai(model=None):
    """Get OpenAI model name - compatibility function."""
    return get_model_name(model)

__all__ = [
    'create_openai_client',
    'get_client_config',
    'get_model_name_openai',
    'get_model_name'
]
