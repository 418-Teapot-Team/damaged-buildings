import requests
from typing import Dict, Any, Optional, Type, TypeVar, Generic
import json
from pydantic import BaseModel

from core.exceptions import (
    ProzorroConnectionError,
    ProzorroResponseError,
    ProzorroParsingError
)
from core.utils import get_required_headers, build_api_url

T = TypeVar('T', bound=BaseModel)


class BaseAPIClient:
    """
    Base class for making API requests to Prozorro.
    
    This class handles the common HTTP operations and response parsing.
    """
    
    def __init__(self, base_url: str = "https://prozorro.gov.ua/api"):
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL for the Prozorro API
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(get_required_headers())
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: The API endpoint
            params: Optional query parameters
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            ProzorroConnectionError: If connection to the API fails
            ProzorroResponseError: If API returns an error status
            ProzorroParsingError: If response parsing fails
        """
        url = build_api_url(self.base_url, endpoint, params)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise ProzorroConnectionError(f"Failed to connect to {url}: {str(e)}")
        except requests.HTTPError as e:
            raise ProzorroResponseError(response.status_code, response.text)
        except json.JSONDecodeError as e:
            raise ProzorroParsingError(f"Failed to parse response from {url}: {str(e)}")
    
    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
              params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: The API endpoint
            data: Optional request data
            params: Optional query parameters
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            ProzorroConnectionError: If connection to the API fails
            ProzorroResponseError: If API returns an error status
            ProzorroParsingError: If response parsing fails
        """
        url = build_api_url(self.base_url, endpoint, params)
        
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise ProzorroConnectionError(f"Failed to connect to {url}: {str(e)}")
        except requests.HTTPError as e:
            raise ProzorroResponseError(response.status_code, response.text)
        except json.JSONDecodeError as e:
            raise ProzorroParsingError(f"Failed to parse response from {url}: {str(e)}")
    
    def get_tender_html(self, tender_id: str) -> str:
        """
        Get the HTML content of a specific tender.
        
        Args:
            tender_id: The ID of the tender
            
        Returns:
            The HTML content of the tender page
            
        Raises:
            ProzorroConnectionError: If connection to the API fails
            ProzorroResponseError: If API returns an error status
        """
        # The Prozorro web page URL format for tenders
        url = f"https://prozorro.gov.ua/tender/{tender_id}"
        
        try:
            # Use a different set of headers for HTML requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.ConnectionError as e:
            raise ProzorroConnectionError(f"Failed to connect to {url}: {str(e)}")
        except requests.HTTPError as e:
            raise ProzorroResponseError(response.status_code, response.text)
    
    def parse_response(self, response_data: Dict[str, Any], model_class: Type[T]) -> T:
        """
        Parse API response into a Pydantic model.
        
        Args:
            response_data: The API response data
            model_class: The Pydantic model class to use for parsing
            
        Returns:
            An instance of the model_class
            
        Raises:
            ProzorroParsingError: If validation fails
        """
        try:
            return model_class.model_validate(response_data)
        except Exception as e:
            raise ProzorroParsingError(f"Failed to validate response data: {str(e)}") 