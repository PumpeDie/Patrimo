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
    Plot a correlation matrix as a heatmap with only lower triangle (no diagonal).
    
    Args:
        correlation_df: DataFrame containing the correlation matrix
        title: Title for the plot
    """
    # Calculate correlation statistics for dynamic scaling
    corr_values = correlation_df.values
    
    # Properly extract lower triangle values
    mask = np.triu(np.ones_like(corr_values, dtype=bool), k=0)
    lower_triangle = corr_values[~mask]
    
    # Calculate statistics
    mean_corr = np.mean(lower_triangle)
    min_corr = np.min(lower_triangle)
    max_corr = np.max(lower_triangle)
    
    # Print correlation statistics
    print(f"\nCorrelation statistics:")
    print(f"  Mean: {mean_corr:.4f}")
    print(f"  Minimum: {min_corr:.4f}")
    print(f"  Maximum: {max_corr:.4f}")
    
    # Determine dynamic range with 20% padding
    vmin = max(-1, min_corr - 0.2 * abs(min_corr))
    vmax = min(1, max_corr + 0.2 * abs(max_corr))
    
    plt.figure(figsize=(10, 8))
    
    # Create a mask for the upper triangle and diagonal
    # Assurer que le masque est de type booléen
    mask = np.triu(np.ones_like(correlation_df, dtype=bool), k=0)
    
    # Draw the heatmap with only lower triangle (no diagonal)
    ax = sns.heatmap(
        correlation_df,
        annot=True,             # Show the correlation values
        mask=mask,              # Only show the lower triangle without diagonal
        cmap='RdBu_r',          # Blue to Red (direct gradient)
        vmin=vmin,              # Use the dynamic minimum value
        vmax=vmax,              # Use the dynamic maximum value
        center=None,            # No centering to have a direct gradient
        square=True,            # Make sure the cells are square
        linewidths=.5,          # Width of the dividing lines
        cbar_kws={"shrink": .5},# Colorbar settings
        fmt=".2f"               # Format for annotations (2 decimal places)
    )
    
    # Adjust labels - create a list of positions for visible ticks
    n = len(correlation_df)
    
    # Keep all positions except first row and last column
    # For X-axis (columns): skip the last position
    xtick_positions = np.arange(n-1) + 0.5
    # For Y-axis (rows): skip the first position
    ytick_positions = np.arange(1, n) + 0.5
    
    # Set only the positions we want to see
    plt.xticks(xtick_positions, correlation_df.columns[:-1], rotation=45, ha='right', fontsize=9)
    plt.yticks(ytick_positions, correlation_df.index[1:], fontsize=9)
    
    plt.title(f"{title}")
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(src_dir, 'data', 'correlation_matrix.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Correlation matrix plot saved to {output_file}")
    
    # Show the plot
    plt.show()
    
    # Return the mean correlation for further use if needed
    return mean_corr

def main():
    """Main function to calculate and display the correlation matrix."""
    try:
        # Create asset manager
        asset_manager = AssetManager()
        
        # Get the correlation matrix
        print("Calculating correlation matrix...")
        correlation, ticker_to_name = asset_manager.get_correlation_matrix(start="2023-01-01", end="2024-12-31")
        
        if correlation.empty:
            print("No data available to calculate correlations.")
            return
        
        # Use shorter names for the columns and index
        shorter_names = {name: name[:20] + '...' if len(name) > 20 else name 
                         for name in correlation.columns}
        correlation.rename(columns=shorter_names, index=shorter_names, inplace=True)
        
        # Print the correlation matrix
        print("\nCorrelation Matrix:")
        print(correlation.round(2))
        
        # Plot the correlation matrix and get mean correlation
        print("\nGenerating correlation heatmap...")
        mean_correlation = plot_correlation_matrix(correlation)
        
        # You can use mean_correlation for additional analysis here
        if mean_correlation > 0.7:
            print("\nAlert: High average correlation (>0.7) indicates poor diversification.")
        elif mean_correlation < 0.3:
            print("\nInfo: Low average correlation (<0.3) indicates good diversification.")
        else:
            print("\nInfo: Moderate average correlation indicates acceptable diversification.")
        
    except ImportError as e:
        print(f"Error: Required package not found. {e}")
        print("Please install required packages: pip install numpy pandas matplotlib seaborn")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()