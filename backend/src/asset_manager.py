"""
Asset Manager module for handling financial assets data retrieval and processing.
"""

import json
import os
import pandas as pd
import yfinance as yf
import numpy as np
from typing import Dict, List, Optional, Tuple

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "data.json")
ETFS_FILE = os.path.join(os.path.dirname(__file__), "data", "etfs.json")

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
        else:
            # For other ISINs, we can try to search for the ticker directly
            search_result = yf.Ticker(isin).info
            if 'symbol' in search_result:
                return search_result['symbol']
        # If no ticker found, return None
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
    
    def get_historical_data(self, tickers: List[str], start: str = "2023-01-01", end : str = "2025-12-16") -> pd.DataFrame:
        """
        Get historical price data and returns for a list of tickers.
        
        Args:
            tickers: List of ticker symbols
            start: Start date for historical data
            end: End date for historical data
            
        Returns:
            DataFrame with returns data (not prices)
        """
        try:
            # Download the data
            data = yf.download(tickers, start=start, end=end, group_by='ticker', progress=False)
            
            if data.empty:
                print("No data downloaded for any ticker")
                return pd.DataFrame()
            
            # For a single ticker, the structure is different
            if len(tickers) == 1:
                ticker = tickers[0]
                data.columns = pd.MultiIndex.from_product([[ticker], data.columns])
            
            # Get close prices in a clean DataFrame
            close_prices = pd.DataFrame()
            for ticker in tickers:
                if (ticker, 'Adj Close') in data.columns:
                    close_prices[ticker] = data[(ticker, 'Adj Close')]
                elif (ticker, 'Close') in data.columns:
                    close_prices[ticker] = data[(ticker, 'Close')]
            
            if close_prices.empty:
                print("No close price data found")
                return pd.DataFrame()
            
            # Remove rows where all values are NaN
            close_prices = close_prices.dropna(how='all')
            
            # Check data availability for each ticker
            print(f"\nData availability check:")
            valid_tickers = []
            for ticker in close_prices.columns:
                non_null_count = close_prices[ticker].count()
                first_valid = close_prices[ticker].first_valid_index()
                last_valid = close_prices[ticker].last_valid_index()
                if non_null_count > 0:
                    print(f" - {ticker}: {non_null_count} days ({first_valid.strftime('%Y-%m-%d')} to {last_valid.strftime('%Y-%m-%d')})")
                    valid_tickers.append(ticker)
                else:
                    print(f" - {ticker}: No data available")
            
            if not valid_tickers:
                print("No tickers with valid data")
                return pd.DataFrame()
            
            # Keep only tickers with data
            close_prices = close_prices[valid_tickers]
            
            # Find the common period where all tickers have data
            # Drop rows where ANY ticker is missing (to ensure proper correlation)
            close_prices_common = close_prices.dropna()
            
            if close_prices_common.empty:
                print("\nWarning: No common period found where all tickers have data")
                print("Calculating with available data (may have gaps)")
                close_prices_common = close_prices
            else:
                print(f"\nCommon period found: {close_prices_common.index[0].strftime('%Y-%m-%d')} to {close_prices_common.index[-1].strftime('%Y-%m-%d')}")
                print(f"Number of common trading days: {len(close_prices_common)}")
            
            # Calculate returns instead of using raw prices
            returns = np.log(close_prices_common / close_prices_common.shift(1)).dropna()
            
            print(f"Calculated returns for {len(returns)} trading days")
            
            return returns
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_correlation_matrix(self, start: str = "2023-01-01", end: str = "2025-12-16") -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Calculate correlation matrix for assets in the ISIN list using returns.
        
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
        
        # Get returns data instead of price data
        returns_data = self.get_historical_data(tickers, start, end)
        
        # Calculate correlation
        if not returns_data.empty:
            # Verify we have enough data points
            print(f"Data points per ticker:")
            for ticker in returns_data.columns:
                print(f" - {ticker}: {returns_data[ticker].count()} valid returns")
            
            correlation = returns_data.corr(method='pearson')
            
            # Rename columns and index to use names instead of tickers
            correlation.columns = [ticker_to_name.get(t, t) for t in correlation.columns]
            correlation.index = [ticker_to_name.get(t, t) for t in correlation.index]
            return correlation, ticker_to_name
        
        return pd.DataFrame(), ticker_to_name
    
    def get_correlation_matrix_from_etfs(self, start: str = "2023-01-01", end: str = "2025-12-16") -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Calculate correlation matrix for ETFs from etfs.json using returns.
        
        Args:
            start: Start date for historical data (YYYY-MM-DD)
            end: End date for historical data (YYYY-MM-DD)
        
        Returns:
            Tuple of (correlation matrix, mapping of tickers to names)
        """
        try:
            with open(ETFS_FILE, 'r') as file:
                etfs_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading etfs.json: {e}")
            return pd.DataFrame(), {}
        
        etfs = etfs_data.get("etfs", [])
        
        if not etfs:
            print("No ETFs found in etfs.json")
            return pd.DataFrame(), {}
        
        tickers = []
        ticker_to_name = {}
        
        # Extract tickers and names directly from etfs.json
        for etf in etfs:
            ticker = etf.get("ticker")
            name = etf.get("name")
            if ticker and name:
                tickers.append(ticker)
                ticker_to_name[ticker] = name
        
        if not tickers:
            print("No valid tickers found in etfs.json")
            return pd.DataFrame(), {}
        
        print(f"Processing {len(tickers)} ETFs: {', '.join(tickers)}")
        
        # Get returns data
        returns_data = self.get_historical_data(tickers, start, end)
        
        # Calculate correlation
        if not returns_data.empty:
            # Verify we have enough data points
            print(f"Data points per ticker:")
            for ticker in returns_data.columns:
                print(f" - {ticker}: {returns_data[ticker].count()} valid returns")
            
            correlation = returns_data.corr(method='pearson')
            
            # Rename columns and index to use names instead of tickers
            correlation.columns = [ticker_to_name.get(t, t) for t in correlation.columns]
            correlation.index = [ticker_to_name.get(t, t) for t in correlation.index]
            return correlation, ticker_to_name
        
        return pd.DataFrame(), ticker_to_name
    