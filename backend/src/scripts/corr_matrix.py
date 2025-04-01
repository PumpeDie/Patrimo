"""
Script for calculating the correlation matrix between ETFs and assets.

This script:
1. Reads ISIN codes from the data file
2. Retrieves ticker symbols for each ISIN
3. Fetches historical price data
4. Calculates and displays the correlation matrix
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add the parent directory to the path to import the AssetManager
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
sys.path.insert(0, src_dir)

from asset_manager import AssetManager

def plot_correlation_matrix(correlation_df, title="Asset Correlation Matrix"):
    """
    Plot a correlation matrix as a heatmap.
    
    Args:
        correlation_df: DataFrame containing the correlation matrix
        title: Title for the plot
    """
    plt.figure(figsize=(10, 8))
    
    # Create a mask for the upper triangle
    mask = ~np.tril(np.ones(correlation_df.shape)).astype(bool)
    
    # Draw the heatmap with the mask
    sns.heatmap(
        correlation_df,
        annot=True,            # Show the correlation values
        mask=mask,             # Only show the lower triangle
        cmap='coolwarm',       # Color map (red for negative, blue for positive)
        vmin=-1, vmax=1,       # Value range
        center=0,              # Center the colormap at 0
        square=True,           # Make sure the cells are square
        linewidths=.5,         # Width of the dividing lines
        cbar_kws={"shrink": .5},  # Colorbar settings
        fmt=".2f"              # Format for annotations (2 decimal places)
    )
    
    plt.title(title)
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(src_dir, 'data', 'correlation_matrix.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Correlation matrix plot saved to {output_file}")
    
    # Show the plot
    plt.show()

def main():
    """Main function to calculate and display the correlation matrix."""
    try:
        # Create asset manager
        asset_manager = AssetManager()
        
        # Get the correlation matrix
        print("Calculating correlation matrix...")
        correlation, ticker_to_name = asset_manager.get_correlation_matrix(period="1y")
        
        if correlation.empty:
            print("No data available to calculate correlations.")
            return
        
        # Print the correlation matrix
        print("\nCorrelation Matrix:")
        print(correlation.round(2))
        
        # Plot the correlation matrix
        print("\nGenerating correlation heatmap...")
        plot_correlation_matrix(correlation)
        
    except ImportError as e:
        print(f"Error: Required package not found. {e}")
        print("Please install required packages: pip install numpy pandas matplotlib seaborn")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()