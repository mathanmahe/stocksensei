from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import google.generativeai as genai
from datetime import datetime
import yfinance as yf
import os
import gradio as gr 
from dotenv import load_dotenv
import pandas as pd
from decimal import Decimal
from pymongo import MongoClient

@dataclass
class ComprehensiveStockInfo:
    # Basic Info
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    
    # Price Information
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    day_low: Optional[float] = None
    day_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    
    # Trading Information
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    avg_volume_10d: Optional[int] = None
    avg_volume_3m: Optional[int] = None
    
    # Market Metrics
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    beta: Optional[float] = None
    
    # Financial Ratios
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    
    # Dividend Information
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    ex_dividend_date: Optional[str] = None
    
    # Financial Metrics
    revenue: Optional[float] = None
    revenue_per_share: Optional[float] = None
    revenue_growth: Optional[float] = None
    gross_profits: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    earnings_growth: Optional[float] = None
    
    # Balance Sheet Metrics
    total_cash: Optional[float] = None
    total_debt: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    
    # Additional Metrics
    shares_outstanding: Optional[int] = None
    float_shares: Optional[int] = None
    held_percent_insiders: Optional[float] = None
    held_percent_institutions: Optional[float] = None
    short_ratio: Optional[float] = None
    short_percent_of_float: Optional[float] = None
    
    # SEC Filings
    sec_filings: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert all non-None values to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

class StockAnalyzer:
    def __init__(self, api_key: str, mongodb_uri: str):
        """Initialize the StockAnalyzer with Gemini API key and MongoDB connection."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.mongo_client = MongoClient(mongodb_uri)
        self.sec_db = self.mongo_client.sec_data

    def _safe_get(self, info: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get a value from the info dictionary."""
        try:
            value = info.get(key, default)
            return None if value in ['-', '', 'nan', float('nan')] else value
        except:
            return default

    def get_sec_filings(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch SEC filings data from MongoDB for a given ticker."""
        filings_collection = self.sec_db.filings
        filings = list(filings_collection.find(
            {"stock_ticker": ticker},
            {
                "filing_type": 1,
                "filing_date": 1,
                "company": 1,
                "filing_description": 1,
                "item_1": 1,
                "item_2": 1,
                "item_3": 1,
                "item_4": 1,
                "item_5": 1,
                "item_6": 1,
                "item_7": 1,
                "item_8": 1,
                "item_9": 1,
                "item_10": 1,
                "item_11": 1,
                "item_12": 1,
                "item_13": 1,
                "item_14": 1,
                "item_15": 1,
                "_id": 0
            }
        ).sort("filing_date", -1).limit(1))
        return filings

    def get_stock_data(self, symbol: str) -> ComprehensiveStockInfo:
        """Fetch comprehensive stock data using yfinance and SEC filings."""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Fetch SEC filings
        sec_filings = self.get_sec_filings(symbol)
        
        stock_info = ComprehensiveStockInfo(
            symbol=symbol,
            company_name=self._safe_get(info, 'longName'),
            sector=self._safe_get(info, 'sector'),
            industry=self._safe_get(info, 'industry'),
            country=self._safe_get(info, 'country'),
            website=self._safe_get(info, 'website'),
            current_price=self._safe_get(info, 'currentPrice'),
            previous_close=self._safe_get(info, 'previousClose'),
            open_price=self._safe_get(info, 'open'),
            day_low=self._safe_get(info, 'dayLow'),
            day_high=self._safe_get(info, 'dayHigh'),
            fifty_two_week_low=self._safe_get(info, 'fiftyTwoWeekLow'),
            fifty_two_week_high=self._safe_get(info, 'fiftyTwoWeekHigh'),
            volume=self._safe_get(info, 'volume'),
            avg_volume=self._safe_get(info, 'averageVolume'),
            avg_volume_10d=self._safe_get(info, 'averageVolume10days'),
            avg_volume_3m=self._safe_get(info, 'averageVolume3month'),
            market_cap=self._safe_get(info, 'marketCap'),
            enterprise_value=self._safe_get(info, 'enterpriseValue'),
            beta=self._safe_get(info, 'beta'),
            pe_ratio=self._safe_get(info, 'trailingPE'),
            forward_pe=self._safe_get(info, 'forwardPE'),
            peg_ratio=self._safe_get(info, 'pegRatio'),
            price_to_book=self._safe_get(info, 'priceToBook'),
            price_to_sales=self._safe_get(info, 'priceToSalesTrailing12Months'),
            dividend_rate=self._safe_get(info, 'dividendRate'),
            dividend_yield=self._safe_get(info, 'dividendYield'),
            ex_dividend_date=self._safe_get(info, 'exDividendDate'),
            revenue=self._safe_get(info, 'totalRevenue'),
            revenue_per_share=self._safe_get(info, 'revenuePerShare'),
            revenue_growth=self._safe_get(info, 'revenueGrowth'),
            gross_profits=self._safe_get(info, 'grossProfits'),
            ebitda=self._safe_get(info, 'ebitda'),
            net_income=self._safe_get(info, 'netIncomeToCommon'),
            earnings_growth=self._safe_get(info, 'earningsGrowth'),
            total_cash=self._safe_get(info, 'totalCash'),
            total_debt=self._safe_get(info, 'totalDebt'),
            total_assets=self._safe_get(info, 'totalAssets'),
            total_liabilities=self._safe_get(info, 'totalDebt'),
            shares_outstanding=self._safe_get(info, 'sharesOutstanding'),
            float_shares=self._safe_get(info, 'floatShares'),
            held_percent_insiders=self._safe_get(info, 'heldPercentInsiders'),
            held_percent_institutions=self._safe_get(info, 'heldPercentInstitutions'),
            short_ratio=self._safe_get(info, 'shortRatio'),
            short_percent_of_float=self._safe_get(info, 'shortPercentOfFloat'),
            sec_filings=sec_filings
        )
        
        return stock_info

    def format_context(self, stock_data: ComprehensiveStockInfo) -> str:
        """Format stock data into a readable context string."""
        data_dict = stock_data.to_dict()
        context_parts = []
        
        categories = {
            "Company Information": ["company_name", "sector", "industry", "country", "website"],
            "Price Information": ["current_price", "previous_close", "open_price", "day_low", "day_high",
                                "fifty_two_week_low", "fifty_two_week_high"],
            "Trading Information": ["volume", "avg_volume", "avg_volume_10d", "avg_volume_3m"],
            "Market Metrics": ["market_cap", "enterprise_value", "beta"],
            "Financial Ratios": ["pe_ratio", "forward_pe", "peg_ratio", "price_to_book", "price_to_sales"],
            "Dividend Information": ["dividend_rate", "dividend_yield", "ex_dividend_date"],
            "Financial Metrics": ["revenue", "revenue_per_share", "revenue_growth", "gross_profits",
                                "ebitda", "net_income", "earnings_growth"],
            "Balance Sheet": ["total_cash", "total_debt", "total_assets", "total_liabilities"],
            "Ownership & Float": ["shares_outstanding", "float_shares", "held_percent_insiders",
                                "held_percent_institutions", "short_ratio", "short_percent_of_float"]
        }

        for category, fields in categories.items():
            category_data = {k: data_dict[k] for k in fields if k in data_dict}
            if category_data:
                context_parts.append(f"\n{category}:")
                for key, value in category_data.items():
                    formatted_key = key.replace('_', ' ').title()
                    if isinstance(value, (float, Decimal)):
                        if key.endswith('_percent') or key in ['dividend_yield']:
                            formatted_value = f"{value:.2f}%"
                        elif value > 1_000_000_000:
                            formatted_value = f"${value/1_000_000_000:.2f}B"
                        elif value > 1_000_000:
                            formatted_value = f"${value/1_000_000:.2f}M"
                        else:
                            formatted_value = f"${value:.2f}"
                    else:
                        formatted_value = str(value)
                    context_parts.append(f"- {formatted_key}: {formatted_value}")
        
        # Add SEC Filings section
        if hasattr(stock_data, 'sec_filings') and stock_data.sec_filings:
            context_parts.append("\nRecent SEC Filings:")
            for filing in stock_data.sec_filings:
                filing_date = filing.get('filing_date', 'N/A')
                filing_type = filing.get('filing_type', 'N/A')
                filing_desc = filing.get('filing_description', 'N/A')
                
                # Add the main filing information
                context_parts.append(f"- {filing_date}: {filing_type} - {filing_desc}")
                
                # Add items 1-15 on separate lines if they exist
                for i in range(1, 16):
                    item_key = f'item_{i}'
                    if filing.get(item_key):
                        context_parts.append(f"  • Item {i}: {filing[item_key]}")
                
                # Add a blank line between filings for better readability
                context_parts.append("")

        return "\n".join(context_parts)

    async def ask_about_stock(self, question: str, symbol: str) -> str:
        """Ask questions about a stock and get AI-generated responses."""
        stock_data = self.get_stock_data(symbol)
        context = self.format_context(stock_data)
        
        prompt = f"""Based on the following comprehensive stock information for {symbol}:
        {context}
        
        Please answer this question: {question}
        
        Provide a detailed analysis based on the available data, highlighting key metrics and their implications."""
        
        response = self.model.generate_content(prompt)
        return response.text

# class StockQAApp:
#     def __init__(self):
#         """Initialize the Stock Q&A Application."""
#         load_dotenv()
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in environment variables")
#         self.analyzer = StockAnalyzer(api_key)
    
#     async def run(self):
#         """Run the interactive Q&A session."""
#         print("Welcome to the Enhanced Stock Q&A!")
#         print("Enter 'quit' to exit")
#         print("\nExample questions:")
#         print("- What's the company's financial health based on these metrics?")
#         print("- How does the current valuation look considering all ratios?")
#         print("- What's the institutional ownership and short interest situation?")
#         print("- How's the company's profitability and growth?")
        
#         while True:
#             symbol = input("\nEnter stock symbol: ").upper()
#             if symbol.lower() == 'quit':
#                 break
                
#             question = input("What would you like to know about this stock? ")
#             if question.lower() == 'quit':
#                 break
            
#             try:
#                 answer = await self.analyzer.ask_about_stock(question, symbol)
#                 print("\nAnalysis:", answer)
#             except Exception as e:
#                 print(f"Error: {str(e)}")
class StockQAApp:
    def __init__(self):
        """Initialize the Stock Q&A Application."""
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        mongodb_uri = os.getenv('MONGODB_URI')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI not found in environment variables")

        self.analyzer = StockAnalyzer(api_key, mongodb_uri)

    def run(self):
        """Run the interactive Q&A session with Gradio UI."""
        with gr.Blocks(theme=gr.themes.Soft()) as interface:
            gr.Markdown(
                """
                # StockSensei: AI-Powered Stock Analysis
                Get detailed insights about any stock including financial metrics, SEC filings, and more.
                """
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    symbol_input = gr.Textbox(
                        label="Stock Symbol",
                        placeholder="e.g., AAPL",
                        lines=1
                    )
                with gr.Column(scale=2):
                    question_input = gr.Textbox(
                        label="Your Question",
                        placeholder="What would you like to know about this stock?",
                        lines=2
                    )
            
            with gr.Row():
                analyze_btn = gr.Button("Analyze", variant="primary")
                clear_btn = gr.Button("Clear")
            
            output = gr.Markdown(
                label="Analysis",
                value="Your analysis will appear here...",
            )
            
            gr.Examples(
                examples=[
                    ["AAPL", "What's the company's financial health based on recent SEC filings and metrics?"],
                    ["MSFT", "How does the current valuation look considering all ratios?"],
                    ["GOOGL", "What's the institutional ownership and recent SEC filing trends?"],
                    ["AMZN", "Analyze the company's profitability, growth, and recent 10-K highlights"],
                ],
                inputs=[symbol_input, question_input],
            )

            def clear_outputs():
                return {
                    symbol_input: "",
                    question_input: "",
                    output: "Your analysis will appear here..."
                }

            async def analyze(symbol: str, question: str) -> str:
                try:
                    result = await self.analyzer.ask_about_stock(question, symbol)
                    return f"### Analysis for {symbol.upper()}\n\n{result}"
                except Exception as e:
                    return f"Error analyzing {symbol.upper()}: {str(e)}"

            analyze_btn.click(
                fn=analyze,
                inputs=[symbol_input, question_input],
                outputs=output
            )
            
            clear_btn.click(
                fn=clear_outputs,
                inputs=[],
                outputs=[symbol_input, question_input, output]
            )

        interface.launch(
            share=False,
            server_name="0.0.0.0",
            server_port=7860
        )

    def ask_stock_question(self, symbol: str, question: str) -> str:
        """Handle stock question input from Gradio."""
        try:
            answer = asyncio.run(self.analyzer.ask_about_stock(question, symbol))
            return answer
        except Exception as e:
            return f"Error: {str(e)}"


async def main():
    """Main entry point for the application."""
    app = StockQAApp()
    app.run()  

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())