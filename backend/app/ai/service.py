from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import httpx
import os
from enum import Enum

class AIProvider(Enum):
    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class AIService(ABC):
    """Abstract base class for AI services"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class LocalAIService(AIService):
    """Local AI service using Ollama or similar local model"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        try:
            print(f"Attempting to generate with model: {self.model}")
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "top_p": kwargs.get("top_p", 0.9),
                        "max_tokens": kwargs.get("max_tokens", 4000)
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            print(f"Generation successful, response length: {len(result.get('response', ''))}")
            return result.get("response", "")
        except Exception as e:
            print(f"Local AI generation failed: {str(e)}")
            raise Exception(f"Local AI generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        try:
            # Quick health check
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                print(f"Ollama health check: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False

class OpenAIService(AIService):
    """OpenAI API service"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1000)
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)

class AnthropicService(AIService):
    """Anthropic Claude API service"""
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            raise Exception(f"Anthropic generation failed: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)

class AIManager:
    """Manager for AI services with fallback support"""
    
    def __init__(self):
        self.services: Dict[AIProvider, Optional[AIService]] = {
            AIProvider.LOCAL: None,
            AIProvider.OPENAI: None,
            AIProvider.ANTHROPIC: None
        }
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize available AI services based on configuration"""
        
        # Initialize local service
        try:
            local_service = LocalAIService()
            if local_service.is_available():
                self.services[AIProvider.LOCAL] = local_service
        except:
            pass
        
        # Initialize OpenAI service
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.services[AIProvider.OPENAI] = OpenAIService(openai_key)
        
        # Initialize Anthropic service
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.services[AIProvider.ANTHROPIC] = AnthropicService(anthropic_key)
    
    async def generate_text(self, prompt: str, preferred_provider: Optional[AIProvider] = None, **kwargs) -> str:
        """Generate text using available AI services with fallback"""
        
        # Try preferred provider first
        if preferred_provider and self.services.get(preferred_provider):
            try:
                return await self.services[preferred_provider].generate_text(prompt, **kwargs)
            except Exception as e:
                print(f"Preferred provider {preferred_provider} failed: {e}")
        
        # Fallback to any available service
        for provider, service in self.services.items():
            if service and service.is_available():
                try:
                    return await service.generate_text(prompt, **kwargs)
                except Exception as e:
                    print(f"Provider {provider} failed: {e}")
                    continue
        
        raise Exception("No AI services available")
    
    def get_available_providers(self) -> list[AIProvider]:
        """Get list of available AI providers"""
        return [
            provider for provider, service in self.services.items() 
            if service and service.is_available()
        ]
    
    def update_api_keys(self, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
        """Update API keys for external services"""
        if openai_key:
            self.services[AIProvider.OPENAI] = OpenAIService(openai_key)
        
        if anthropic_key:
            self.services[AIProvider.ANTHROPIC] = AnthropicService(anthropic_key)

# Global AI manager instance
ai_manager = AIManager()