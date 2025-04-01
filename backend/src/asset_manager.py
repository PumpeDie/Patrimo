"""
Asset Manager module for handling financial assets data retrieval and processing.
"""

import json
import os
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "data.json")

class AssetManager:
    """
    Manages assets data, including ISIN code conversion, data retrieval, and caching.
    """
    
    def __init__(self):
        """Initialize the asset manager with data from the JSON file."""
        self.data = self._load_data()
        
    def _load_data(self) -> dict:
        """Load data from the JSON file."""
        try:
            with open(DATA_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default structure if file doesn't exist or is invalid
            return {"isin_list": [], "tickers_cache": {}, "names_cache": {}}
    
    def _save_data(self) -> None:
        """Save data to the JSON file."""
        with open(DATA_FILE, 'w') as file:
            json.dump(self.data, file, indent=2)
    
    def get_isin_list(self) -> List[str]:
        """Get the list of ISIN codes."""
        return self.data.get("isin_list", [])
    
    def add_isin(self, isin: str) -> None:
        """Add an ISIN code to the list."""
        if "isin_list" not in self.data:
            self.data["isin_list"] = []
        
        if isin not in self.data["isin_list"]:
            self.data["isin_list"].append(isin)
            self._save_data()
            
    def remove_isin(self, isin: str) -> None:
        """Remove an ISIN code from the list."""
        if "isin_list" in self.data and isin in self.data["isin_list"]:
            self.data["isin_list"].remove(isin)
            self._save_data()
    
    def get_ticker_from_isin(self, isin: str) -> Optional[str]:
        """
        Get the ticker symbol for an ISIN code. Uses cache if available.
        """
        # Check if ticker is in cache
        if isin in self.data.get("tickers_cache", {}):
            return self.data["tickers_cache"][isin]
        
        # If not in cache, fetch it (implementation depends on available APIs)
        # For simplicity, we'll use a Yahoo Finance workaround
        # This is not always reliable and might need to be replaced with a better API
        try:
            # Simple conversion for well-known French stocks/ETFs
            # In real implementation, this should use a proper ISIN to ticker API
            ticker = self._isin_to_ticker_conversion(isin)
            
            if ticker:
                # Save to cache
                if "tickers_cache" not in self.data:
                    self.data["tickers_cache"] = {}
                self.data["tickers_cache"][isin] = ticker
                self._save_data()
                return ticker
        except Exception as e:
            print(f"Error fetching ticker for {isin}: {e}")
            
        return None
    
    def _isin_to_ticker_conversion(self, isin: str) -> Optional[str]:
        """
        Convert ISIN to ticker using Yahoo Finance search.
        This is a simplified version and might not work for all ISINs.
        """
        # For French stocks, we can try a simple .PA suffix
        if isin.startswith("FR"):
            # Try to search for the ISIN
            search_result = yf.Ticker(isin).info
            if 'symbol' in search_result:
                return search_result['symbol']
                
            # If not found, try some common mappings
            # This would need to be expanded or replaced with a proper API
            common_mappings = {
                "FR0011550193": "PAEEM.PA",  # Amundi MSCI Emerging Markets ETF
                "FR0011550185": "PAASI.PA",  # Amundi MSCI Pacific ex Japan ETF
                "FR0013380607": "EESM.PA",   # BNP Paribas Easy ECPI Global ESG Med Tech ETF
                "FR0013412012": "EUBS.PA",   # BNP Paribas Easy ECPI Circular Economy Leaders ETF
                "FR0013411980": "ESG5.PA"    # BNP Paribas Easy ECPI Global ESG Blue Economy ETF
            }
            
            if isin in common_mappings:
                return common_mappings[isin]
        
        return None
    
    def get_asset_name(self, isin: str, ticker: Optional[str] = None) -> Optional[str]:
        """
        Get the human-readable name of an asset from its ISIN or ticker.
        """
        # Check cache first
        if isin in self.data.get("names_cache", {}):
            return self.data["names_cache"][isin]
        
        # If ticker not provided, try to get it
        if not ticker:
            ticker = self.get_ticker_from_isin(isin)
        
        if not ticker:
            return None
        
        # Fetch from Yahoo Finance
        try:
            asset_info = yf.Ticker(ticker).info
            if 'shortName' in asset_info:
                name = asset_info['shortName']
                
                # Save to cache
                if "names_cache" not in self.data:
                    self.data["names_cache"] = {}
                self.data["names_cache"][isin] = name
                self._save_data()
                
                return name
        except Exception as e:
            print(f"Error fetching name for {ticker} ({isin}): {e}")
            
        return None
    
    def get_historical_data(self, tickers: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Get historical price data for a list of tickers.
        
        Args:
            tickers: List of ticker symbols
            period: Period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with price data
        """
        try:
            data = yf.download(tickers, period=period, group_by='ticker')
            # For a single ticker, the structure is different
            if len(tickers) == 1:
                ticker = tickers[0]
                data.columns = pd.MultiIndex.from_product([[ticker], data.columns])
            
            # Reformat to get just the close prices in a clean DataFrame
            close_prices = pd.DataFrame()
            for ticker in tickers:
                if (ticker, 'Close') in data.columns:
                    close_prices[ticker] = data[(ticker, 'Close')]
            
            return close_prices
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_correlation_matrix(self, period: str = "1y") -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Calculate correlation matrix for assets in the ISIN list.
        
        Returns:
            Tuple of (correlation matrix, mapping of tickers to names)
        """
        isin_list = self.get_isin_list()
        tickers = []
        ticker_to_name = {}
        ticker_to_isin = {}
        
        # Get tickers for all ISINs
        for isin in isin_list:
            ticker = self.get_ticker_from_isin(isin)
            if ticker:
                tickers.append(ticker)
                name = self.get_asset_name(isin, ticker) or ticker
                ticker_to_name[ticker] = name
                ticker_to_isin[ticker] = isin
        
        if not tickers:
            return pd.DataFrame(), {}
        
        # Get historical data
        price_data = self.get_historical_data(tickers, period)
        
        # Calculate correlation
        if not price_data.empty:
            correlation = price_data.corr()
            # Rename columns and index to use names instead of tickers
            correlation.columns = [ticker_to_name.get(t, t) for t in correlation.columns]
            correlation.index = [ticker_to_name.get(t, t) for t in correlation.index]
            return correlation, ticker_to_name
        
        return pd.DataFrame(), ticker_to_name
    