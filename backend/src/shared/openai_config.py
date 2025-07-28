"""
Module to handle global OpenAI API key configuration
"""

# Global variable to store OpenAI API key
OPENAI_API_KEY_GLOBAL = None

def set_openai_api_key(api_key: str):
    """Set the global OpenAI API key"""
    global OPENAI_API_KEY_GLOBAL
    OPENAI_API_KEY_GLOBAL = api_key

def get_openai_api_key():
    """Get the global OpenAI API key"""
    global OPENAI_API_KEY_GLOBAL
    return OPENAI_API_KEY_GLOBAL

def clear_openai_api_key():
    """Clear the global OpenAI API key"""
    global OPENAI_API_KEY_GLOBAL
    OPENAI_API_KEY_GLOBAL = None 