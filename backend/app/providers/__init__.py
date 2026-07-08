from app.providers.base import AIProvider
from app.providers.openrouter import OpenRouterProvider
from app.providers.deepseek import DeepseekProvider

def get_provider(provider_name: str, api_key: str = None, model: str = None) -> AIProvider:
    provider_name = (provider_name or "").lower()
    
    if provider_name == "deepseek":
        return DeepseekProvider(api_key=api_key, model=model)
    elif provider_name == "openrouter":
        return OpenRouterProvider(api_key=api_key, model=model)
    else:
        # Default fallback
        return OpenRouterProvider(api_key=api_key, model=model)
