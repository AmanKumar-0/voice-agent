"""Configuration and constants for the voice agent."""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration."""
    
    # LiveKit
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    
    # Speech Services
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter").lower()  # openai, openrouter, together, ollama (default: ollama for local)
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")  # For custom endpoints
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Together AI
    TOGETHER_API_KEY: Optional[str] = os.getenv("TOGETHER_API_KEY")
    TOGETHER_BASE_URL: str = os.getenv("TOGETHER_BASE_URL", "https://api.together.xyz/v1")
    
    # Ollama (Local)
    # Ollama's OpenAI-compatible API is at http://localhost:11434/v1/chat/completions
    # The OpenAI library will append /chat/completions, so base_url should be /v1
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # Default model
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://xfkhrjlffkimiubzdcwi.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "sb_publishable_ZiOCRh0kKP3g4rYE7nFlVw_d2ZIHa7n")
    
    # Avatar Service (Beyond Presence)
    BEYOND_PRESENCE_API_KEY: Optional[str] = os.getenv("BEYOND_PRESENCE_API_KEY")
    BEYOND_PRESENCE_AVATAR_ID: Optional[str] = os.getenv("BEYOND_PRESENCE_AVATAR_ID")  # Avatar ID from Beyond Presence
    # TAVUS_API_KEY: Optional[str] = os.getenv("TAVUS_API_KEY")
    
    # Server
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")  # Empty = use provider default
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))  # Timeout in seconds (default: 120, higher for Ollama)
    
    # Cost rates (per unit)
    DEEPGRAM_RATE_PER_MINUTE: float = 0.0043
    OPENAI_RATE_PER_1K_TOKENS: float = 0.03  # GPT-4o approximate
    CARTESIA_RATE_PER_CHAR: float = 0.00001
    AVATAR_RATE_PER_MINUTE: float = 0.05
    
    # Note: OpenRouter, Together AI, and Ollama costs are calculated dynamically
    # based on the provider selected
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default model based on provider."""
        if cls.LLM_MODEL:
            return cls.LLM_MODEL
        
        defaults = {
            "openai": "gpt-4o",
            # openai/gpt-4o-mini
            "openrouter": "openai/gpt-4o-mini",  # or "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b-instruct"
            "together": "meta-llama/Llama-3.1-70B-Instruct-Turbo",
            "ollama": cls.OLLAMA_MODEL,  # Default: qwen2.5:7b
        }
        return defaults.get(cls.LLM_PROVIDER, "gpt-4o")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required = [
            cls.LIVEKIT_URL,
            cls.LIVEKIT_API_KEY,
            cls.LIVEKIT_API_SECRET,
            cls.DEEPGRAM_API_KEY,
            cls.CARTESIA_API_KEY,
            cls.SUPABASE_URL,
            cls.SUPABASE_KEY,
            cls.OPENROUTER_API_KEY,
            cls.LLM_PROVIDER
        ]
        
        # Validate LLM provider configuration
        if cls.LLM_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set when LLM_PROVIDER=openai")
        elif cls.LLM_PROVIDER == "openrouter":
            if not cls.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY must be set when LLM_PROVIDER=openrouter")
        elif cls.LLM_PROVIDER == "together":
            if not cls.TOGETHER_API_KEY:
                raise ValueError("TOGETHER_API_KEY must be set when LLM_PROVIDER=together")
        elif cls.LLM_PROVIDER == "ollama":
            # Ollama doesn't require API key, but we should validate URL is reachable
            pass
        else:
            raise ValueError(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be one of: openai, openrouter, together, ollama")
        
        if not all(required):
            missing = [k for k, v in {
                "LIVEKIT_URL": cls.LIVEKIT_URL,
                "LIVEKIT_API_KEY": cls.LIVEKIT_API_KEY,
                "LIVEKIT_API_SECRET": cls.LIVEKIT_API_SECRET,
                "DEEPGRAM_API_KEY": cls.DEEPGRAM_API_KEY,
                "CARTESIA_API_KEY": cls.CARTESIA_API_KEY,
                "SUPABASE_URL": cls.SUPABASE_URL,
                "SUPABASE_KEY": cls.SUPABASE_KEY,
            }.items() if not v]
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
