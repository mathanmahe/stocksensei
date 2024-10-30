import json
from pathlib import Path
from sec_cik_mapper import StockMapper

# Script to add ticker symbol to the dataset. 

# Initialize the stock mapper
mapper = StockMapper()

# Path to the JSON files directory
json_dir = Path("data/10-K")

def pad_cik(cik: int) -> str:
    """Convert CIK to a 10-digit zero-padded string."""
    return str(cik).zfill(10)

def add_stock_ticker_to_json(file_path: Path, mapper):
    """Add stock ticker to JSON file based on CIK."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Check if 'cik' key exists and pad to 10 digits
    if "cik" in data:
        cik_padded = pad_cik(data["cik"])
        tickers = mapper.cik_to_tickers.get(cik_padded)

        # If ticker found, add it to the JSON data
        if tickers:
            # Assuming we only take the first ticker if multiple are present
            data["stock_ticker"] = list(tickers)[0]

            # Write back the updated JSON data
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Updated {file_path.name} with ticker {data['stock_ticker']} for company {data['company']}")
        else:
            print(f"No ticker found for CIK {cik_padded} in {file_path.name}")
    else:
        print(f"No 'cik' field found in {file_path.name}")

# Process all JSON files in the directory
for json_file in json_dir.glob("*.json"):
    add_stock_ticker_to_json(json_file, mapper)
