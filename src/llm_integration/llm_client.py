"""
LLM Client
Abstraction layer for Claude and GPT-4 APIs
"""
import os
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def chat(self, messages: List[Dict], system_prompt: str = None) -> str:
        """Send a chat completion request"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the client is properly configured"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT-4 client"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key) and self.client is not None
    
    def chat(self, messages: List[Dict], system_prompt: str = None) -> str:
        if not self.is_available():
            return "Error: OpenAI client not available. Please check your API key."
        
        try:
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        self.client = None
        
        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key) and self.client is not None
    
    def chat(self, messages: List[Dict], system_prompt: str = None) -> str:
        if not self.is_available():
            return "Error: Anthropic client not available. Please check your API key."
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt or "",
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"


class LLMClient:
    """
    Unified LLM Client that supports both OpenAI and Anthropic
    Automatically selects the available provider
    """
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM client
        
        Args:
            provider: "openai", "anthropic", or None for auto-detection
        """
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
        
        # Initialize clients
        self.openai_client = OpenAIClient()
        self.anthropic_client = AnthropicClient()
        
        # Select active client
        self.active_client = self._select_client()
    
    def _select_client(self) -> BaseLLMClient:
        """Select the appropriate client based on availability and preference"""
        if self.provider == "anthropic" and self.anthropic_client.is_available():
            return self.anthropic_client
        elif self.provider == "openai" and self.openai_client.is_available():
            return self.openai_client
        elif self.openai_client.is_available():
            return self.openai_client
        elif self.anthropic_client.is_available():
            return self.anthropic_client
        else:
            return None
    
    def is_available(self) -> bool:
        """Check if any LLM is available"""
        return self.active_client is not None and self.active_client.is_available()
    
    def get_provider_name(self) -> str:
        """Get the name of the active provider"""
        if isinstance(self.active_client, OpenAIClient):
            return "OpenAI GPT-4"
        elif isinstance(self.active_client, AnthropicClient):
            return "Anthropic Claude"
        return "None"
    
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        Send a chat message to the LLM
        
        Args:
            user_message: The user's message/query
            system_prompt: Optional system prompt for context
            
        Returns:
            LLM response text
        """
        if not self.is_available():
            return self._get_fallback_response()
        
        messages = [{"role": "user", "content": user_message}]
        return self.active_client.chat(messages, system_prompt)
    
    def chat_with_context(self, 
                         user_message: str, 
                         context: str,
                         system_prompt: str = None) -> str:
        """
        Send a chat message with additional context
        
        Args:
            user_message: The user's query
            context: Contract text or clause context
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        if not self.is_available():
            return self._get_fallback_response()
        
        full_message = f"""Context (Contract Text):
---
{context}
---

Question/Request:
{user_message}"""
        
        messages = [{"role": "user", "content": full_message}]
        return self.active_client.chat(messages, system_prompt)
    
    def _get_fallback_response(self) -> str:
        """Return a fallback response when no LLM is available"""
        return """⚠️ AI-powered analysis is not available.

To enable AI features, please configure an API key:
1. Copy .env.example to .env
2. Add your OpenAI or Anthropic API key
3. Restart the application

The contract analysis will continue using rule-based methods only."""
