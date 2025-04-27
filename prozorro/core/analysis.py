"""
Data analysis utilities for extracted tender data.

This module provides functions to analyze and generate insights from extracted 
tender data. It can be used to identify patterns, trends, and other useful
information from the tender data.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the loaded JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON data from {file_path}: {str(e)}")
        return {}


def load_all_json_data(directory: str) -> List[Dict[str, Any]]:
    """
    Load all JSON files from a directory.
    
    Args:
        directory: Path to the directory containing JSON files
        
    Returns:
        List of dictionaries, each containing data from a JSON file
    """
    data = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                json_data = load_json_data(file_path)
                if json_data:
                    data.append(json_data)
        logger.info(f"Loaded {len(data)} JSON files from {directory}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON data from directory {directory}: {str(e)}")
        return []


def analyze_regions(tenders: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze the regions where tenders are located.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary mapping regions to the number of tenders in each region
    """
    regions = Counter()
    
    for tender in tenders:
        # Try to get region from location data
        if 'location' in tender and 'region' in tender['location']:
            region = tender['location']['region']
            regions[region] += 1
        # Try to get region from customer data
        elif 'customer' in tender and 'region' in tender['customer']:
            region = tender['customer']['region']
            regions[region] += 1
        # Try to get region from subject data
        elif 'subject' in tender and 'delivery_place' in tender['subject']:
            delivery_place = tender['subject']['delivery_place']
            region_match = re.search(r'Україна,\s+(.*?(?:область|місто|Київ|Крим))', delivery_place)
            if region_match:
                region = region_match.group(1).strip()
                regions[region] += 1
    
    # Convert Counter to dict
    return dict(regions.most_common())


def analyze_procurement_types(tenders: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze the types of procurement procedures used.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary mapping procurement types to the number of tenders using each type
    """
    procurement_types = Counter()
    
    for tender in tenders:
        if 'procurement_type' in tender:
            procurement_type = tender['procurement_type']
            procurement_types[procurement_type] += 1
    
    return dict(procurement_types.most_common())


def analyze_tender_categories(tenders: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze the categories of products/services being procured.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary mapping categories to the number of tenders in each category
    """
    categories = Counter()
    
    for tender in tenders:
        if 'subject' in tender and 'classifier_name' in tender['subject']:
            category = tender['subject']['classifier_name']
            categories[category] += 1
    
    return dict(categories.most_common())


def analyze_suppliers(tenders: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the suppliers (winners) of tenders.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary mapping supplier names to information about their tenders
    """
    suppliers = defaultdict(lambda: {
        'tender_count': 0,
        'total_value': 0,
        'currencies': set(),
        'tender_ids': set()
    })
    
    for tender in tenders:
        if 'awards' in tender and tender['awards']:
            for award in tender['awards']:
                if 'participant_name' in award and award['decision'] == 'Переможець':
                    supplier_name = award['participant_name']
                    suppliers[supplier_name]['tender_count'] += 1
                    
                    if 'tender_id' in tender:
                        suppliers[supplier_name]['tender_ids'].add(tender['tender_id'])
                    
                    if 'bid_amount' in award and 'bid_currency' in award:
                        suppliers[supplier_name]['total_value'] += award['bid_amount']
                        suppliers[supplier_name]['currencies'].add(award['bid_currency'])
    
    # Convert sets to lists for JSON serialization
    for supplier in suppliers.values():
        supplier['currencies'] = list(supplier['currencies'])
        supplier['tender_ids'] = list(supplier['tender_ids'])
    
    return dict(suppliers)


def analyze_customers(tenders: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the customers (procuring entities) of tenders.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary mapping customer names to information about their tenders
    """
    customers = defaultdict(lambda: {
        'tender_count': 0,
        'total_value': 0,
        'currencies': set(),
        'tender_ids': set(),
        'edrpou': None,
        'region': None
    })
    
    for tender in tenders:
        if 'customer' in tender and 'name' in tender['customer']:
            customer_name = tender['customer']['name']
            customers[customer_name]['tender_count'] += 1
            
            if 'tender_id' in tender:
                customers[customer_name]['tender_ids'].add(tender['tender_id'])
            
            if 'expected_cost' in tender:
                cost = tender['expected_cost']
                customers[customer_name]['total_value'] += cost.get('amount', 0)
                customers[customer_name]['currencies'].add(cost.get('currency', 'UAH'))
            
            if 'edrpou' in tender['customer'] and not customers[customer_name]['edrpou']:
                customers[customer_name]['edrpou'] = tender['customer']['edrpou']
            
            if 'region' in tender['customer'] and not customers[customer_name]['region']:
                customers[customer_name]['region'] = tender['customer']['region']
    
    # Convert sets to lists for JSON serialization
    for customer in customers.values():
        customer['currencies'] = list(customer['currencies'])
        customer['tender_ids'] = list(customer['tender_ids'])
    
    return dict(customers)


def analyze_tender_values(tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the monetary values of tenders.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary containing various statistics about tender values
    """
    values = {
        'total': 0,
        'count': 0,
        'average': 0,
        'min': float('inf'),
        'max': 0,
        'currency': 'UAH',
        'by_year': defaultdict(int),
        'by_month': defaultdict(int),
        'by_category': defaultdict(int)
    }
    
    for tender in tenders:
        if 'expected_cost' in tender and 'amount' in tender['expected_cost']:
            amount = tender['expected_cost']['amount']
            values['total'] += amount
            values['count'] += 1
            values['min'] = min(values['min'], amount)
            values['max'] = max(values['max'], amount)
            
            # Extract year and month from tender date if available
            if 'dates' in tender and 'publication_date' in tender['dates']:
                date_str = tender['dates']['publication_date']
                try:
                    # Try different date formats
                    date_formats = [
                        '%d %B %Y',  # 01 січня 2023
                        '%d %b %Y',  # 01 січ 2023
                        '%d.%m.%Y',  # 01.01.2023
                    ]
                    
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_date:
                        year = parsed_date.year
                        month = parsed_date.month
                        values['by_year'][str(year)] += amount
                        values['by_month'][f"{year}-{month:02d}"] += amount
                except Exception as e:
                    logger.debug(f"Could not parse date {date_str}: {str(e)}")
            
            # Group by category
            if 'subject' in tender and 'classifier_name' in tender['subject']:
                category = tender['subject']['classifier_name']
                values['by_category'][category] += amount
    
    # Calculate average
    if values['count'] > 0:
        values['average'] = values['total'] / values['count']
    
    # Reset min if no tenders were found
    if values['min'] == float('inf'):
        values['min'] = 0
    
    # Convert defaultdicts to regular dicts
    values['by_year'] = dict(values['by_year'])
    values['by_month'] = dict(values['by_month'])
    values['by_category'] = dict(values['by_category'])
    
    return values


def analyze_damaged_buildings(tenders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify and analyze tenders related to damaged buildings.
    
    This function looks for keywords related to damaged buildings, damage repair,
    reconstruction, etc. in tender titles and descriptions.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        List of tenders related to damaged buildings with additional analysis
    """
    # Keywords related to damaged buildings or repairs (in Ukrainian)
    keywords = [
        'пошкодж', 'руйнув', 'зруйнов', 'відновл', 'реконструкц', 
        'відбудов', 'ремонт', 'віднов', 'реставрац', 'відбудов'
    ]
    
    damaged_building_tenders = []
    
    for tender in tenders:
        is_damaged_building = False
        matched_keywords = set()
        
        # Check title
        if 'title' in tender:
            title = tender['title'].lower()
            for keyword in keywords:
                if keyword in title:
                    is_damaged_building = True
                    matched_keywords.add(keyword)
        
        # Check description
        if 'subject' in tender and 'description' in tender['subject']:
            description = tender['subject']['description'].lower()
            for keyword in keywords:
                if keyword in description:
                    is_damaged_building = True
                    matched_keywords.add(keyword)
        
        if is_damaged_building:
            # Add analysis data to the tender
            tender_copy = tender.copy()
            tender_copy['analysis'] = {
                'is_damaged_building': True,
                'matched_keywords': list(matched_keywords)
            }
            damaged_building_tenders.append(tender_copy)
    
    return damaged_building_tenders


def generate_summary_report(tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a comprehensive summary report from tender data.
    
    Args:
        tenders: List of tender data dictionaries
        
    Returns:
        Dictionary containing various analyses and statistics
    """
    report = {
        'tender_count': len(tenders),
        'regions': analyze_regions(tenders),
        'procurement_types': analyze_procurement_types(tenders),
        'categories': analyze_tender_categories(tenders),
        'values': analyze_tender_values(tenders),
        'top_suppliers': dict(sorted(
            analyze_suppliers(tenders).items(), 
            key=lambda x: x[1]['total_value'], 
            reverse=True
        )[:10]),
        'top_customers': dict(sorted(
            analyze_customers(tenders).items(), 
            key=lambda x: x[1]['total_value'], 
            reverse=True
        )[:10]),
        'damaged_buildings': {
            'count': len(analyze_damaged_buildings(tenders))
        }
    }
    
    return report


def save_analysis_report(report: Dict[str, Any], output_file: str) -> None:
    """
    Save an analysis report to a JSON file.
    
    Args:
        report: Dictionary containing the analysis report
        output_file: Path to save the report to
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved analysis report to {output_file}")
    except Exception as e:
        logger.error(f"Error saving analysis report to {output_file}: {str(e)}") 