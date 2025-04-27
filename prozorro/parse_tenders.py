#!/usr/bin/env python3
import os
import json
import logging
import argparse
from pathlib import Path
from core.html_parser import parse_tender_html_file

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_single_tender(html_file_path: str, output_file: str = None) -> None:
    """
    Parse a single tender HTML file and print the extracted data.
    
    Args:
        html_file_path: Path to the HTML file
        output_file: Optional path to save JSON output to
    """
    logger.info(f"Parsing tender file: {html_file_path}")
    
    # Parse the HTML file
    parsed_data = parse_tender_html_file(html_file_path)
    
    # Convert to JSON
    json_data = json.dumps(parsed_data, ensure_ascii=False, indent=2)
    
    # Save to file if requested
    if output_file:
        logger.info(f"Saving parsed data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
    
    # Print JSON data
    print(json_data)
    
    # Print summary
    print("\n--- Tender Summary ---")
    if 'title' in parsed_data:
        print(f"Title: {parsed_data.get('title')}")
    if 'tender_id' in parsed_data:
        print(f"ID: {parsed_data.get('tender_id')}")
    if 'status' in parsed_data:
        print(f"Status: {parsed_data.get('status')}")
    if 'expected_cost' in parsed_data:
        cost = parsed_data.get('expected_cost')
        print(f"Expected cost: {cost.get('amount')} {cost.get('currency')}")
    if 'customer' in parsed_data and 'name' in parsed_data['customer']:
        print(f"Customer: {parsed_data['customer'].get('name')}")
    if 'awards' in parsed_data and parsed_data['awards']:
        winner = parsed_data['awards'][0]
        print(f"Winner: {winner.get('participant_name')}")
        print(f"Bid amount: {winner.get('bid_amount')} {winner.get('bid_currency', '')}")
    
    num_data_points = sum(1 for _ in _iter_dict_values(parsed_data))
    logger.info(f"Extracted {num_data_points} data points from tender")


def parse_all_tenders(input_dir: str, output_dir: str) -> None:
    """
    Parse all HTML files in the input directory and save results to output directory.
    
    Args:
        input_dir: Directory containing HTML files
        output_dir: Directory to save parsed JSON files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all HTML files
    html_files = list(Path(input_dir).glob('*.html'))
    logger.info(f"Found {len(html_files)} HTML files to parse")
    
    # Process each file
    for i, html_file in enumerate(html_files):
        # Determine output file path
        output_file = os.path.join(output_dir, f"{html_file.stem}.json")
        
        try:
            # Parse the HTML file
            parsed_data = parse_tender_html_file(str(html_file))
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[{i+1}/{len(html_files)}] Parsed {html_file.name} -> {output_file}")
        except Exception as e:
            logger.error(f"Error processing {html_file.name}: {str(e)}")
    
    logger.info(f"Finished parsing {len(html_files)} HTML files")


def _iter_dict_values(d, parent_key=''):
    """Helper function to iterate through all values in a nested dictionary."""
    if isinstance(d, dict):
        for k, v in d.items():
            key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                yield from _iter_dict_values(v, key)
            else:
                yield key, v
    elif isinstance(d, list):
        for i, item in enumerate(d):
            key = f"{parent_key}[{i}]"
            if isinstance(item, (dict, list)):
                yield from _iter_dict_values(item, key)
            else:
                yield key, item


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Prozorro tender HTML files")
    parser.add_argument("--file", help="Path to a single HTML file to parse")
    parser.add_argument("--output", help="Path to save the JSON output")
    parser.add_argument("--input-dir", help="Directory containing HTML files to parse")
    parser.add_argument("--output-dir", help="Directory to save parsed JSON files")
    
    args = parser.parse_args()
    
    if args.file:
        # Parse a single file
        parse_single_tender(args.file, args.output)
    elif args.input_dir and args.output_dir:
        # Parse all files in directory
        parse_all_tenders(args.input_dir, args.output_dir)
    else:
        # Use default example
        example_file = os.path.join("output", "UA-2023-06-07-005367-a.html")
        if os.path.exists(example_file):
            parse_single_tender(example_file)
        else:
            logger.error(f"Example file not found: {example_file}")
            parser.print_help() 