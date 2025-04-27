from typing import Dict, Any, Optional
import urllib.parse
from urllib.parse import urlencode


def build_api_url(
    base_url: str, 
    endpoint: str, 
    query_params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a complete API URL with query parameters.
    
    Args:
        base_url: The base URL of the API
        endpoint: The API endpoint
        query_params: Optional query parameters
        
    Returns:
        The complete URL with encoded query parameters
    """
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    if query_params:
        # Filter out None values
        filtered_params = {k: v for k, v in query_params.items() if v is not None}
        if filtered_params:
            query_string = urlencode(filtered_params)
            url = f"{url}?{query_string}"
            
    return url


def encode_text_param(text: str) -> str:
    """
    Properly encode a text parameter for URL usage.
    
    Args:
        text: The text to encode
        
    Returns:
        The URL-encoded text
    """
    return urllib.parse.quote(text)


def get_required_headers() -> Dict[str, str]:
    """
    Return the minimum set of headers required for the Prozorro API.
    
    Returns:
        Dictionary of required headers
    """
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    } 