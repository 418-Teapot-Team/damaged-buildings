#!/usr/bin/env python3
import os
import json
import logging
import argparse
from pathlib import Path
from core.analysis import (
    load_all_json_data, 
    generate_summary_report, 
    save_analysis_report,
    analyze_damaged_buildings,
    analyze_regions
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(input_dir: str, output_dir: str) -> None:
    """
    Analyze tender data and generate reports.
    
    Args:
        input_dir: Directory containing parsed tender JSON files
        output_dir: Directory to save analysis reports to
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all tender data
    logger.info(f"Loading tender data from {input_dir}")
    tenders = load_all_json_data(input_dir)
    if not tenders:
        logger.error("No tender data found, exiting")
        return
    
    logger.info(f"Loaded {len(tenders)} tenders")
    
    logger.info("Generating summary report")
    summary_report = generate_summary_report(tenders)
    
    summary_file = os.path.join(output_dir, "summary_report.json")
    save_analysis_report(summary_report, summary_file)
    
    # Identify tenders related to damaged buildings
    logger.info("Identifying tenders related to damaged buildings")
    damaged_building_tenders = analyze_damaged_buildings(tenders)
    logger.info(f"Found {len(damaged_building_tenders)} tenders related to damaged buildings")
    
    damaged_buildings_file = os.path.join(output_dir, "damaged_buildings.json")
    try:
        with open(damaged_buildings_file, 'w', encoding='utf-8') as f:
            json.dump(damaged_building_tenders, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved damaged buildings data to {damaged_buildings_file}")
    except Exception as e:
        logger.error(f"Error saving damaged buildings data: {str(e)}")
    
    # Analyze regions
    logger.info("Analyzing regions")
    regions = analyze_regions(tenders)
    regions_file = os.path.join(output_dir, "regions.json")
    try:
        with open(regions_file, 'w', encoding='utf-8') as f:
            json.dump(regions, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved regions data to {regions_file}")
    except Exception as e:
        logger.error(f"Error saving regions data: {str(e)}")
    
    # Print summary
    print("\n===== TENDER ANALYSIS SUMMARY =====")
    print(f"Total tenders analyzed: {summary_report['tender_count']}")
    print(f"Total value of tenders: {summary_report['values']['total']} UAH")
    print(f"Average tender value: {summary_report['values']['average']:.2f} UAH")
    print(f"Tenders related to damaged buildings: {len(damaged_building_tenders)}")
    
    print("\nTop 5 regions by tender count:")
    for region, count in list(regions.items())[:5]:
        print(f"  - {region}: {count} tenders")
    
    print("\nTop 5 procurement categories:")
    for category, count in list(summary_report['categories'].items())[:5]:
        print(f"  - {category}: {count} tenders")
    
    print("\nTop 5 suppliers by value:")
    for supplier, data in list(summary_report['top_suppliers'].items())[:5]:
        print(f"  - {supplier}: {data['total_value']} UAH ({data['tender_count']} tenders)")
    
    print("\nResults saved to:")
    print(f"  - Summary report: {summary_file}")
    print(f"  - Damaged buildings data: {damaged_buildings_file}")
    print(f"  - Regions data: {regions_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze tender data and generate reports")
    parser.add_argument("--input-dir", required=False, default="../parsed_data",
                        help="Directory containing parsed tender JSON files")
    parser.add_argument("--output-dir", required=False, default="../analysis_results",
                        help="Directory to save analysis reports to")
    
    args = parser.parse_args()
    
    main(args.input_dir, args.output_dir) 