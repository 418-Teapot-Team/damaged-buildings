import os
import logging
from typing import Dict, Any, Optional, List, Union, Tuple

from openai import OpenAI

from core.models import Tender
from core.exceptions import ProzorroAPIError

logger = logging.getLogger(__name__)


class AIAnalysisError(Exception):
    """Exception raised when AI analysis fails."""
    pass


class BuildingAnalyzer:
    """
    Class for analyzing tender data using OpenAI's language models to identify
    building-related tenders.
    
    This class is independent of the Prozorro service and can process tender results
    returned by the Prozorro scraper.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the building analyzer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use for analysis
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI analysis will not work.")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    def is_building_related(self, tender_title: str) -> bool:
        """
        Analyze if a tender is related to building/house/flats repairs or construction.
        
        Args:
            tender_title: The title of the tender to analyze
            
        Returns:
            Tuple containing:
            - Boolean indicating if the tender is building-related
            - Confidence score (0.0-1.0)
            - Explanation for the decision
            
        Raises:
            AIAnalysisError: If the analysis fails
        """
        if not self.client:
            raise AIAnalysisError("OpenAI API key not provided. Cannot perform analysis.")
        
        try:
            prompt = f"""
            Analyze the text and determine if it's related to restoring or building buildings, houses, 
            apartments, flats.
            Text: "{tender_title}"

            Respond with a text YES or NO.
            Only one word in response, no other text.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "text"},
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing public procurement tenders."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.choices[0].message.content.strip()
            if response_text not in ["YES", "NO"]:
                raise AIAnalysisError("Invalid response from OpenAI API")
            
            return response_text == "YES"
            
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze tender: {str(e)}")
    
    def filter_building_related_tenders(
        self, 
        tenders: List[Tender], 
    ) -> List[Tender]:
        """
        Filter tenders to find those related to buildings/houses/flats.
        
        Args:
            tenders: List of Tender objects to analyze
            
        Returns:
            List of Tender objects that are building-related
        """
        logger.info(f"Analyzing {len(tenders)} tenders for building relation...")
        
        return [tender for tender in tenders if self.is_building_related(tender.title)]
    