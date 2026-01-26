"""LLM factory for creating LLM instances based on configuration."""
import logging
from typing import Optional
from livekit.agents import llm
from livekit.plugins import openai
from config import Config

logger = logging.getLogger(__name__)


def create_llm() -> llm.LLM:
    """Create an LLM instance based on configuration."""
    provider = Config.LLM_PROVIDER.lower()
    model = Config.get_default_model()
    temperature = Config.LLM_TEMPERATURE
    
    if provider == "openai":
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        kwargs = {
            "model": model,
            "temperature": temperature,
            "api_key": Config.OPENAI_API_KEY,
        }
        
        if Config.OPENAI_BASE_URL:
            kwargs["base_url"] = Config.OPENAI_BASE_URL
        
        return openai.LLM(**kwargs)
    
    elif provider == "openrouter":
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        # OpenRouter uses OpenAI-compatible API
        # Limit max_tokens to 4000 to avoid credit issues with free accounts
        return openai.LLM(
            model=model,
            temperature=temperature,
            api_key=Config.OPENROUTER_API_KEY,
            base_url=Config.OPENROUTER_BASE_URL,
            # max_tokens=4000,  # Limit to avoid credit errors
            # OpenRouter requires HTTP Referer header
            # extra_headers={
            #     "HTTP-Referer": "https://github.com/your-repo",  # Update with your repo URL
            #     "X-Title": "Voice Agent",
            # },
        )
    
    elif provider == "together":
        if not Config.TOGETHER_API_KEY:
            raise ValueError("TOGETHER_API_KEY not configured")
        
        # Together AI uses OpenAI-compatible API
        return openai.LLM(
            model=model,
            temperature=temperature,
            api_key=Config.TOGETHER_API_KEY,
            base_url=Config.TOGETHER_BASE_URL,
        )
    
    elif provider == "ollama":
        # Ollama uses OpenAI-compatible API locally
        # The base URL should include /v1 as OpenAI SDK appends /chat/completions
        # Ollama can be slow, especially with larger models
        # The LiveKit framework will retry automatically on timeout
        ollama_model = Config.OLLAMA_MODEL if not Config.LLM_MODEL else Config.LLM_MODEL
        
        logger.info(f"Creating Ollama LLM with model: {ollama_model}")
        logger.info(f"Note: Ollama may be slow. Timeout warnings are expected and will be retried automatically.")
        
        return openai.LLM(
            model=ollama_model,
            temperature=temperature,
            api_key="ollama",  # Ollama doesn't require real API key
            base_url=Config.OLLAMA_BASE_URL,
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def validate_llm_config() -> bool:
    """Validate LLM configuration."""
    try:
        provider = Config.LLM_PROVIDER.lower()
        
        if provider == "openai" and not Config.OPENAI_API_KEY:
            return False
        elif provider == "openrouter" and not Config.OPENROUTER_API_KEY:
            return False
        elif provider == "together" and not Config.TOGETHER_API_KEY:
            return False
        elif provider == "ollama":
            # Ollama doesn't need API key, but we could check if server is reachable
            return True
        
        return True
    except Exception as e:
        logger.error(f"Error validating LLM config: {e}")
        return False
