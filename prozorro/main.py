import logging
import os
from core import ProzorroScraper
from ai_analyzer import BuildingAnalyzer
from dotenv import load_dotenv

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_output_dir():
    """Create the output directory if it doesn't exist."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    return output_dir

def save_tender_html(tender_id, html_content, output_dir):
    """Save tender HTML content to a file."""
    filename = f"{output_dir}/{tender_id}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    logging.info(f"Saved HTML for tender {tender_id} to {filename}")

def main():
    setup_logging()
    # load .env
    load_dotenv()
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        logging.warning("OPENAI_API_KEY environment variable not set. AI analysis will not work.")
    
    # Create output directory
    output_dir = create_output_dir()
    
    scraper = ProzorroScraper()
    building_analyzer = BuildingAnalyzer(api_key=openai_api_key)
    
    search_text = "обстріл"
    regions = "61-64"
    per_page = 20
    max_pages = None  # Set to None to get all pages
    
    try:
        logging.info(f"Starting tender search with text='{search_text}', regions={regions}")
        
        # Get all tenders using pagination
        all_tenders = scraper.get_all_tender_pages(
            text=search_text,
            region=regions,
            per_page=per_page,
            max_pages=max_pages
        )
        
        logging.info(f"Retrieved a total of {len(all_tenders)} tenders")
        
        # Filter for building-related tenders
        building_tenders = building_analyzer.filter_building_related_tenders(all_tenders)
        logging.info(f"Found {len(building_tenders)} building-related tenders")
        
        # Save HTML for all building-related tenders
        for tender in building_tenders:
            try:
                html_content = scraper.get_tender_html(tender.tender_id)
                save_tender_html(tender.tender_id, html_content, output_dir)
                
            except Exception as e:
                logging.error(f"Error saving HTML for tender {tender.tender_id}: {str(e)}")
        
        logging.info(f"Process completed. Saved HTML for {len(building_tenders)} building-related tenders to {output_dir}/")
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
