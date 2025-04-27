# Prozorro Tender Data Parser and Analyzer

This project provides tools to parse HTML tender pages from the Prozorro procurement system and analyze the extracted data to generate insights. It's particularly focused on analyzing tenders related to damaged buildings.

## Project Structure

- `prozorro/core/html_parser.py` - HTML parser for extracting structured data from tender pages
- `prozorro/core/analysis.py` - Analysis utilities for generating insights from parsed data
- `prozorro/parse_tenders.py` - Script to parse HTML tender pages and save the extracted data as JSON
- `prozorro/analyze_tenders.py` - Script to analyze parsed data and generate reports
- `output/` - Directory containing HTML tender pages
- `parsed_data/` - Directory where parsed JSON data is stored
- `analysis_results/` - Directory where analysis reports are stored

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd damaged-buildings
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Parsing Tender HTML Files

To parse a single HTML file:

```
cd prozorro
python parse_tenders.py --file ../output/UA-2023-06-07-005367-a.html --output ../parsed_data/UA-2023-06-07-005367-a.json
```

To parse all HTML files in a directory:

```
cd prozorro
python parse_tenders.py --input-dir ../output --output-dir ../parsed_data
```

### Analyzing Parsed Data

To analyze parsed data and generate reports:

```
cd prozorro
python analyze_tenders.py --input-dir ../parsed_data --output-dir ../analysis_results
```

## Data Structure

### Parsed Tender Data

The parser extracts the following information from tender HTML pages:

- Tender title, ID, and hash
- Tender status and procurement type
- Expected cost and currency
- Customer (procuring entity) information
- Tender subject information (classifier code, description, delivery place, etc.)
- Award information (winner, bid amount, etc.)
- Document links
- Location data (region, city, etc.)

### Analysis Reports

The analysis generates several reports:

- `summary_report.json` - Overall summary of tenders, including total value, top suppliers, etc.
- `damaged_buildings.json` - Tenders identified as related to damaged buildings
- `regions.json` - Distribution of tenders by region

## Example Analysis Results

From the current dataset, the analysis has revealed:

- **Total Tenders:** 139
- **Total Value:** 111,826,045.45 UAH
- **Average Tender Value:** 804,503.92 UAH
- **Tenders Related to Damaged Buildings:** 131
- **Top Region:** Kharkiv Oblast (100 tenders)
- **Top Supplier:** "ПРИВАТНЕ ПІДПРИЄМСТВО 'БУДІВЕЛЬНО-ПРОЕКТНА КОМПАНІЯ 'ФОРСАЙТ'" with 11 million UAH across 11 tenders

## Further Development

Potential areas for further development:

1. Improved location extraction using NLP techniques
2. Temporal analysis to track trends over time
3. Integration with GIS systems for geographic visualization
4. Sentiment analysis of tender descriptions
5. Enhanced damaged building detection using machine learning

## Dependencies

- Python 3.6+
- BeautifulSoup4
- lxml
- requests
- pydantic
- python-dotenv

## License

[License information] 