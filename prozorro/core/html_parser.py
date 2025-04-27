from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TenderHTMLParser:
    """
    Parser for extracting data from Prozorro tender HTML pages.
    
    This class provides methods to extract structured data from HTML content
    of Prozorro tender pages for further analysis.
    """
    
    def __init__(self, html_content: str):
        """
        Initialize the parser with HTML content.
        
        Args:
            html_content: Raw HTML content of the tender page
        """
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.tender_data = {}
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse the HTML content and extract all available data.
        
        Returns:
            A dictionary containing extracted tender data
        """
        try:
            # Extract basic tender information
            self._extract_basic_info()
            
            # Extract customer (procuring entity) information
            self._extract_customer_info()
            
            # Extract tender subject information
            self._extract_subject_info()
            
            # Extract award information
            self._extract_award_info()
            
            # Extract dates
            self._extract_dates()
            
            # Extract documents
            self._extract_documents()
            
            # Extract location data (for geographic analysis)
            self._extract_location_data()
            
            # Clean up and normalize data
            self._clean_and_normalize_data()
            
            return self.tender_data
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            # Return whatever data we've extracted so far
            return self.tender_data
    
    def _extract_basic_info(self) -> None:
        """Extract basic tender information like ID, title, and status."""
        try:
            # Extract tender title
            title_elem = self.soup.select_one('.tender--head--title')
            if title_elem:
                self.tender_data['title'] = title_elem.get_text(strip=True)
            
            # Extract tender ID and hash
            tender_id_elem = self.soup.select_one('.tender--head--inf')
            if tender_id_elem:
                text = tender_id_elem.get_text(strip=True)
                id_match = re.search(r'(UA-\d{4}-\d{2}-\d{2}-\d{6}-\w)', text)
                hash_match = re.search(r'([a-f0-9]{32})', text)
                
                if id_match:
                    self.tender_data['tender_id'] = id_match.group(1)
                if hash_match:
                    self.tender_data['tender_hash'] = hash_match.group(1)
            
            # Extract tender status
            status_elem = self.soup.select_one('.tender--head--inf .marked')
            if status_elem:
                self.tender_data['status'] = status_elem.get_text(strip=True)
            
            # Extract expected cost
            cost_elem = self.soup.select_one('.tender--description--cost--number')
            if cost_elem:
                cost_text = cost_elem.get_text(strip=True)
                cost_match = re.search(r'([\d\s,.]+)\s*([A-Z]+)', cost_text)
                if cost_match:
                    amount = cost_match.group(1).replace(' ', '').replace(',', '.')
                    currency = cost_match.group(2)
                    self.tender_data['expected_cost'] = {
                        'amount': float(amount),
                        'currency': currency
                    }
            
            # Extract procurement type
            procurement_type_elem = self.soup.select_one('.tender--head--inf')
            if procurement_type_elem:
                for text_part in procurement_type_elem.get_text(strip=True).split('\n'):
                    if 'Закупівля' in text_part:
                        self.tender_data['procurement_type'] = text_part.strip()
                        break
        except Exception as e:
            logger.error(f"Error extracting basic info: {str(e)}")
    
    def _extract_customer_info(self) -> None:
        """Extract information about the customer (procuring entity)."""
        try:
            customer_section = self.soup.select_one('.tender--customer--inner')
            if not customer_section:
                return
            
            customer_info = {}
            
            # Extract customer name
            name_row = customer_section.find('tr', string=lambda s: 'Найменування' in str(s) if s else False)
            if name_row:
                name_cell = name_row.find_all('td')
                if len(name_cell) > 1:
                    customer_info['name'] = name_cell[1].get_text(strip=True)
            
            # Extract EDRPOU (company ID)
            edrpou_row = customer_section.find('tr', string=lambda s: 'ЄДРПОУ' in str(s) if s else False)
            if edrpou_row:
                edrpou_cell = edrpou_row.find_all('td')
                if len(edrpou_cell) > 1:
                    customer_info['edrpou'] = edrpou_cell[1].get_text(strip=True)
            
            # Extract location
            location_row = customer_section.find('tr', string=lambda s: 'Місцезнаходження' in str(s) if s else False)
            if location_row:
                location_cell = location_row.find_all('td')
                if len(location_cell) > 1:
                    location_text = location_cell[1].get_text(strip=True)
                    customer_info['location'] = location_text
                    
                    # Try to extract region from location
                    region_match = re.search(r'Україна[,\s]+(.*?обл\.)', location_text)
                    if region_match:
                        customer_info['region'] = region_match.group(1).strip()
            
            # Extract contact person
            contact_row = customer_section.find('tr', string=lambda s: 'Контактна особа' in str(s) if s else False)
            if contact_row:
                contact_cell = contact_row.find_all('td')
                if len(contact_cell) > 1:
                    contact_text = contact_cell[1].get_text('\n', strip=True).split('\n')
                    if len(contact_text) >= 1:
                        customer_info['contact_name'] = contact_text[0]
                    if len(contact_text) >= 2:
                        customer_info['contact_phone'] = contact_text[1]
                    if len(contact_text) >= 3:
                        customer_info['contact_email'] = contact_text[2]
            
            # Extract category
            category_row = customer_section.find('tr', string=lambda s: 'Категорія' in str(s) if s else False)
            if category_row:
                category_cell = category_row.find_all('td')
                if len(category_cell) > 1:
                    customer_info['category'] = category_cell[1].get_text(strip=True)
            
            self.tender_data['customer'] = customer_info
        except Exception as e:
            logger.error(f"Error extracting customer info: {str(e)}")
            self.tender_data['customer'] = {}
    
    def _extract_subject_info(self) -> None:
        """Extract information about the tender subject."""
        try:
            subject_section = self.soup.select_one('.col-sm-9 .margin-bottom.margin-bottom-more')
            if not subject_section:
                return
            
            subject_info = {}
            
            # Extract subject type
            type_elem = subject_section.find('p', string=lambda s: 'Вид предмету закупівлі' in str(s) if s else False)
            if type_elem:
                type_match = re.search(r'Вид предмету закупівлі:\s*(.+)', type_elem.get_text(strip=True))
                if type_match:
                    subject_info['type'] = type_match.group(1)
            
            # Extract classifier code
            classifier_elem = subject_section.find('p', string=lambda s: 'Класифікатор' in str(s) if s else False)
            if classifier_elem:
                classifier_text = classifier_elem.get_text(strip=True)
                classifier_match = re.search(r'ДК 021:2015:(\d+):([^:]+)', classifier_text)
                if classifier_match:
                    subject_info['classifier_code'] = classifier_match.group(1)
                    subject_info['classifier_name'] = classifier_match.group(2).strip()
            
            # Extract delivery information
            delivery_elem = subject_section.find('div', string=lambda s: 'Місце поставки товарів' in str(s) if s else False)
            if delivery_elem:
                delivery_text = delivery_elem.get_text(strip=True)
                delivery_match = re.search(r'Місце поставки товарів або місце виконання робіт чи надання послуг:\s*(.+)', delivery_text)
                if delivery_match:
                    subject_info['delivery_place'] = delivery_match.group(1)
            
            # Extract delivery deadline
            deadline_elem = subject_section.find('div', string=lambda s: 'Строк поставки товарів' in str(s) if s else False)
            if deadline_elem:
                deadline_text = deadline_elem.get_text(strip=True)
                deadline_match = re.search(r'Строк поставки товарів, виконання робіт чи надання послуг:\s*(.+)', deadline_text)
                if deadline_match:
                    subject_info['delivery_deadline'] = deadline_match.group(1)
            
            # Extract description
            description_elem = subject_section.select_one('.tender--description--text.description')
            if description_elem:
                subject_info['description'] = description_elem.get_text(strip=True)
            
            # Extract quantity
            quantity_elem = subject_section.select_one('.col-md-4 .padding.margin-bottom')
            if quantity_elem:
                subject_info['quantity'] = quantity_elem.get_text(strip=True)
            
            self.tender_data['subject'] = subject_info
        except Exception as e:
            logger.error(f"Error extracting subject info: {str(e)}")
            self.tender_data['subject'] = {}
    
    def _extract_award_info(self) -> None:
        """Extract information about tender awards (winners)."""
        try:
            award_table = self.soup.select_one('.table.table-striped')
            if not award_table:
                return
            
            awards = []
            
            # Process each row in the award table
            for row in award_table.select('tbody tr'):
                cells = row.select('td')
                if len(cells) < 4:
                    continue
                    
                award = {}
                
                # Extract winner name and EDRPOU
                participant_cell = cells[0]
                participant_text = participant_cell.get_text('\n', strip=True).split('\n')
                if len(participant_text) >= 1:
                    award['participant_name'] = participant_text[0]
                if len(participant_text) >= 2:
                    edrpou_match = re.search(r'#(\d+)', participant_text[1])
                    if edrpou_match:
                        award['participant_edrpou'] = edrpou_match.group(1)
                
                # Extract award decision
                decision_cell = cells[1]
                award['decision'] = decision_cell.get_text(strip=True)
                
                # Extract bid amount
                bid_cell = cells[2]
                bid_text = bid_cell.get_text('\n', strip=True).split('\n')
                if len(bid_text) >= 1:
                    try:
                        bid_amount = float(bid_text[0].replace(' ', '').replace(',', '.'))
                        award['bid_amount'] = bid_amount
                    except (ValueError, TypeError):
                        pass
                if len(bid_text) >= 2:
                    currency_match = re.search(r'([A-Z]+)', bid_text[1])
                    if currency_match:
                        award['bid_currency'] = currency_match.group(1)
                
                # Extract publication date
                date_cell = cells[3]
                date_text = date_cell.get_text(strip=True)
                award['publication_date'] = date_text
                
                awards.append(award)
            
            self.tender_data['awards'] = awards
        except Exception as e:
            logger.error(f"Error extracting award info: {str(e)}")
            self.tender_data['awards'] = []
    
    def _extract_dates(self) -> None:
        """Extract various dates related to the tender."""
        try:
            dates = {}
            
            # Extract publication date
            publication_elem = self.soup.find('div', string=lambda s: 'Дата оприлюднення' in str(s) if s else False)
            if publication_elem:
                date_span = publication_elem.select_one('.date')
                if date_span:
                    dates['publication_date'] = date_span.get_text(strip=True)
            
            self.tender_data['dates'] = dates
        except Exception as e:
            logger.error(f"Error extracting dates: {str(e)}")
            self.tender_data['dates'] = {}
    
    def _extract_documents(self) -> None:
        """Extract links to tender documents."""
        try:
            documents = []
            
            # Find document tables
            doc_tables = self.soup.select('.documents-tabs .tender--customer')
            
            for table in doc_tables:
                for row in table.select('tr'):
                    cells = row.select('td')
                    if len(cells) < 2:
                        continue
                    
                    doc = {}
                    
                    # Extract document date
                    date_cell = cells[0]
                    date_div = date_cell.select_one('.date')
                    if date_div:
                        doc['date'] = date_div.get_text(strip=True)
                    
                    # Extract document title and link
                    doc_cell = cells[1]
                    doc_link = doc_cell.select_one('a')
                    if doc_link:
                        doc['title'] = doc_link.get_text(strip=True)
                        doc['url'] = doc_link.get('href', '')
                    
                    documents.append(doc)
            
            self.tender_data['documents'] = documents
        except Exception as e:
            logger.error(f"Error extracting documents: {str(e)}")
            self.tender_data['documents'] = []
    
    def _extract_location_data(self) -> None:
        """Extract location data for geographic analysis."""
        try:
            location_data = {}
            
            # Try to extract from subject delivery place
            if 'subject' in self.tender_data and 'delivery_place' in self.tender_data['subject']:
                delivery_place = self.tender_data['subject']['delivery_place']
                
                # Extract postal code
                postal_code_match = re.search(r'^(\d{5})', delivery_place)
                if postal_code_match:
                    location_data['postal_code'] = postal_code_match.group(1)
                
                # Extract region
                region_match = re.search(r'Україна,\s+(.*?(?:область|місто|Київ|Крим))', delivery_place)
                if region_match:
                    location_data['region'] = region_match.group(1).strip()
                
                # Extract city/locality
                city_match = re.search(r'(?:область|місто|Київ|Крим),\s+(.*?район|.*?місто|.*?смт|.*?селище|.*?село)', delivery_place)
                if city_match:
                    location_data['locality'] = city_match.group(1).strip()
            
            # If we have location data, add it to the tender data
            if location_data:
                self.tender_data['location'] = location_data
        except Exception as e:
            logger.error(f"Error extracting location data: {str(e)}")
    
    def _clean_and_normalize_data(self) -> None:
        """Clean and normalize extracted data."""
        try:
            # Normalize date formats
            if 'dates' in self.tender_data:
                dates = self.tender_data['dates']
                for key, value in dates.items():
                    if value and isinstance(value, str):
                        # Remove extra whitespace
                        dates[key] = ' '.join(value.split())
            
            # Clean up award publication dates
            if 'awards' in self.tender_data and self.tender_data['awards']:
                for award in self.tender_data['awards']:
                    if 'publication_date' in award and award['publication_date']:
                        # Fix broken date formatting (e.g., "07 червня 202313:24")
                        date_str = award['publication_date']
                        if ':' in date_str:
                            parts = re.match(r'(.*?)(\d{4})(\d{2}:\d{2})', date_str)
                            if parts:
                                award['publication_date'] = f"{parts.group(1)} {parts.group(2)} {parts.group(3)}"
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
    
    def to_json(self) -> str:
        """
        Convert parsed data to JSON string.
        
        Returns:
            JSON string representation of the parsed data
        """
        return json.dumps(self.tender_data, ensure_ascii=False, indent=2)


def parse_tender_html(html_content: str) -> Dict[str, Any]:
    """
    Parse a Prozorro tender HTML page and extract structured data.
    
    Args:
        html_content: Raw HTML content of the tender page
        
    Returns:
        Dictionary with extracted tender data
    """
    parser = TenderHTMLParser(html_content)
    return parser.parse()


def parse_tender_html_file(html_file_path: str) -> Dict[str, Any]:
    """
    Parse a Prozorro tender HTML file and extract structured data.
    
    Args:
        html_file_path: Path to the HTML file
        
    Returns:
        Dictionary with extracted tender data
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return parse_tender_html(html_content)
    except Exception as e:
        logger.error(f"Error parsing HTML file {html_file_path}: {str(e)}")
        return {} 