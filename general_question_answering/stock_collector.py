from typing import List, Set, Dict, Any
import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import asyncio
from tqdm import tqdm
import time
from dataclasses import asdict
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='stock_collector.log'
)

class StockDataCollector:
    def __init__(self, mongodb_uri: str, db_name: str = "stock_data"):
        """Initialize the stock data collector."""
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.stocks_collection = self.db.stocks
        self.metadata_collection = self.db.metadata
        
        # Create index
        self.stocks_collection.create_index("symbol", unique=True)
    
    def get_index_components(self) -> Set[str]:
        """Get components of major indices."""
        indices = {
            '^GSPC': 'S&P 500',
            '^NDX': 'NASDAQ-100',
            '^DJI': 'Dow Jones',
            '^RUT': 'Russell 2000'
        }
        
        components = set()
        for index_symbol in indices.keys():
            try:
                index = yf.Ticker(index_symbol)
                if hasattr(index, 'components'):
                    components.update(index.components)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logging.error(f"Error fetching components for {index_symbol}: {str(e)}")
        
        # Add some popular stocks manually in case they're not in the indices
        additional_stocks = {
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NFLX', 'NVDA', 'TSLA',
            'BRK-B', 'JPM', 'V', 'WMT', 'PG', 'JNJ', 'XOM', 'BAC'
        }
        components.update(additional_stocks)
        
        return components

    def _process_stock(self, symbol: str) -> Dict[str, Any]:
        """Process a single stock."""
        try:
            from main import StockAnalyzer  # Import the StockAnalyzer from main script
            analyzer = StockAnalyzer("")  # Empty API key as we don't need Gemini here
            stock_data = analyzer.get_stock_data(symbol)
            
            # Convert to dictionary and add metadata
            stock_dict = asdict(stock_data)
            stock_dict['last_updated'] = datetime.utcnow()
            stock_dict['symbol'] = symbol
            
            return stock_dict
        except Exception as e:
            logging.error(f"Error processing {symbol}: {str(e)}")
            return None

    def collect_stock_data(self) -> None:
        """Collect and store stock data in MongoDB."""
        components = self.get_index_components()
        logging.info(f"Found {len(components)} stocks to process")
        
        # Process stocks in parallel with a thread pool
        with ThreadPoolExecutor(max_workers=5) as executor:
            for stock_dict in tqdm(
                executor.map(self._process_stock, components),
                total=len(components)
            ):
                if stock_dict:
                    try:
                        self.stocks_collection.update_one(
                            {'symbol': stock_dict['symbol']},
                            {'$set': stock_dict},
                            upsert=True
                        )
                    except Exception as e:
                        logging.error(f"Error saving {stock_dict['symbol']}: {str(e)}")
                time.sleep(0.5)  # Rate limiting
        
        # Update metadata
        self.metadata_collection.update_one(
            {'_id': 'collection_metadata'},
            {
                '$set': {
                    'last_update': datetime.utcnow(),
                    'total_stocks': self.stocks_collection.count_documents({})
                }
            },
            upsert=True
        )
        
        logging.info("Stock data collection completed")

def main():
    """Main function to run the collector."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        raise ValueError("MONGODB_URI not found in environment variables")
    
    collector = StockDataCollector(mongodb_uri)
    collector.collect_stock_data()

if __name__ == "__main__":
    main()