from typing import List, Dict, Any, Optional, Union, Tuple
import logging
import time
from core.base import BaseAPIClient
from core.models import TenderSearchResponse, SearchParams, Tender
from core.utils import encode_text_param


class ProzorroScraper(BaseAPIClient):
    """
    A class for scraping data from the Prozorro public procurement API.
    
    This class provides methods to search for tenders and retrieve tender details.
    """
    
    def __init__(self, base_url: str = "https://prozorro.gov.ua/api"):
        """
        Initialize the Prozorro scraper.
        
        Args:
            base_url: The base URL for the Prozorro API
        """
        super().__init__(base_url)
        self.logger = logging.getLogger(__name__)
    
    def search_tenders(
        self,
        text: Optional[str] = None,
        region: Optional[str] = None,
        page: int = 0,
        per_page: int = 20
    ) -> TenderSearchResponse:
        """
        Search for tenders using the Prozorro API.
        
        Args:
            text: Optional search text
            region: Optional region filter (format: '61-64' for regions 61 through 64)
            page: Page number (0-based)
            per_page: Number of results per page
            
        Returns:
            A TenderSearchResponse object containing search results
            
        Raises:
            ProzorroAPIError: If the API request fails
        """
        # Prepare search parameters
        search_params = SearchParams(
            text=text,
            region=region,
            page=page,
            per_page=per_page
        )
        
        # Convert to dict for URL params
        params = search_params.model_dump(exclude_none=True)
        
        self.logger.info(f"Searching tenders with params: {params}")
        
        # Make the POST request to the search endpoint
        response_data = self._post("search/tenders", params=params)
        
        # Parse the response
        return self.parse_response(response_data, TenderSearchResponse)
    
    def get_all_tender_pages(
        self,
        text: Optional[str] = None,
        region: Optional[str] = None,
        per_page: int = 20,
        max_pages: Optional[int] = None
    ) -> List[Tender]:
        """
        Retrieve all pages of tender search results.
        
        Args:
            text: Optional search text
            region: Optional region filter
            per_page: Number of results per page
            max_pages: Maximum number of pages to retrieve (None for all)
            
        Returns:
            A list of Tender objects
            
        Raises:
            ProzorroAPIError: If the API request fails
        """
        results = []
        page = 1
        total_pages = None
        
        while True:
            # Get the current page of results
            response = self.search_tenders(text, region, page, per_page)
            
            # Add the tenders to our results
            results.extend(response.data)
            
            # Calculate total pages if this is the first request
            if total_pages is None:
                total_pages = (response.total + per_page - 1) // per_page
            
            # Logging
            self.logger.info(f"Retrieved page {page}/{total_pages} with {len(response.data)} tenders")
            
            # Check if we've reached the end
            page += 1
            if page >= total_pages:
                break
                
            # Check if we've reached the maximum number of pages
            if max_pages is not None and page >= max_pages:
                self.logger.info(f"Reached maximum number of pages ({max_pages})")
                break

            # add a delay between requests
            time.sleep(1)
        
        return results
        
    def get_tender_html(self, tender_id: str) -> str:
        """
        Get the HTML content for a specific tender.
        
        Args:
            tender_id: The ID of the tender
            
        Returns:
            The HTML content of the tender page
            
        Raises:
            ProzorroConnectionError: If connection fails
            ProzorroResponseError: If API returns an error status
        """
        self.logger.info(f"Getting HTML for tender {tender_id}")
        return super().get_tender_html(tender_id) 