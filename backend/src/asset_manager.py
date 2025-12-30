"""
Asset Manager module for handling financial assets data retrieval and processing.
"""

import json
import os
import pandas as pd
import yfinance as yf
import numpy as np
from typing import Dict, List, Optional, Tuple

ETFS_FILE = os.path.join(os.path.dirname(__file__), "data", "etfs.json")

class AssetManager:
    """
    Manages ETF data retrieval and portfolio correlation analysis.
    """
    
    def __init__(self):
        """Initialize the asset manager."""
        pass
    
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
    
    def _calculate_correlation_from_returns(self, returns_data: pd.DataFrame, ticker_to_name: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Calculate correlation matrix from returns data.
        
        Args:
            returns_data: DataFrame containing returns data
            ticker_to_name: Mapping of tickers to names
        
        Returns:
            Tuple of (correlation matrix, mapping of tickers to names)
        """
        if returns_data.empty:
            return pd.DataFrame(), ticker_to_name
        
        # Verify data points
        print(f"Data points per ticker:")
        for ticker in returns_data.columns:
            print(f" - {ticker}: {returns_data[ticker].count()} valid returns")
        
        # Calculate correlation
        correlation = returns_data.corr(method='pearson')
        
        # Rename columns and index to use names instead of tickers
        correlation.columns = [ticker_to_name.get(t, t) for t in correlation.columns]
        correlation.index = [ticker_to_name.get(t, t) for t in correlation.index]
        
        return correlation, ticker_to_name
    
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
        
        # Calculate and return correlation
        return self._calculate_correlation_from_returns(returns_data, ticker_to_name)
    