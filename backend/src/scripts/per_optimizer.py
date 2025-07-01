"""
PER (Plan d'Épargne Retraite) Optimizer Script

This script calculates the optimal amount to invest in a PER based on salary
and tax optimization, following French tax brackets for 2024.
"""

import os
import sys
from typing import Dict, List, Tuple
import pandas as pd

# Add the parent directory to import AssetManager if needed
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
sys.path.insert(0, src_dir)

class PEROptimizer:
    """
    Calculates optimal PER investment based on French tax brackets and salary.
    """
    
    # French tax brackets for 2024
    TAX_BRACKETS_2024 = [
        {"min": 0, "max": 11294, "rate": 0.0},
        {"min": 11294, "max": 28797, "rate": 0.11},
        {"min": 28797, "max": 82341, "rate": 0.30},
        {"min": 82341, "max": 177106, "rate": 0.41},
        {"min": 177106, "max": float('inf'), "rate": 0.45}
    ]
    
    def __init__(self):
        """Initialize the PER optimizer."""
        pass
    
    def calculate_tax_on_income(self, taxable_income: float) -> float:
        """
        Calculate income tax based on French tax brackets.
        
        Args:
            taxable_income: Net taxable income in euros
            
        Returns:
            Total tax amount in euros
        """
        total_tax = 0.0
        
        for bracket in self.TAX_BRACKETS_2024:
            if taxable_income <= bracket["min"]:
                break
                
            taxable_in_bracket = min(taxable_income, bracket["max"]) - bracket["min"]
            if taxable_in_bracket > 0:
                total_tax += taxable_in_bracket * bracket["rate"]
        
        return total_tax
    
    def get_marginal_tax_rate(self, taxable_income: float) -> float:
        """
        Get the marginal tax rate for a given income.
        
        Args:
            taxable_income: Net taxable income in euros
            
        Returns:
            Marginal tax rate as a decimal (e.g., 0.30 for 30%)
        """
        for bracket in self.TAX_BRACKETS_2024:
            if bracket["min"] <= taxable_income <= bracket["max"]:
                return bracket["rate"]
        return 0.0
    
    def calculate_per_optimization(self, gross_salary: float, 
                                 abatement_rate: float = 0.10,
                                 target_tmi: float = 0.30) -> Dict:
        """
        Calculate optimal PER investment to reach a target tax bracket.
        
        Args:
            gross_salary: Annual gross salary in euros
            abatement_rate: Professional expense deduction rate (default 10%)
            target_tmi: Target marginal tax rate to reach (default 30%)
            
        Returns:
            Dictionary with optimization results
        """
        # Calculate net taxable income
        abatement_amount = gross_salary * abatement_rate
        net_taxable_income = gross_salary - abatement_amount
        
        # Calculate initial tax
        initial_tax = self.calculate_tax_on_income(net_taxable_income)
        initial_marginal_rate = self.get_marginal_tax_rate(net_taxable_income)
        
        # Find the threshold for target TMI
        target_threshold = None
        for bracket in self.TAX_BRACKETS_2024:
            if bracket["rate"] == target_tmi:
                target_threshold = bracket["max"]
                break
        
        if target_threshold is None or net_taxable_income <= target_threshold:
            return {
                "gross_salary": gross_salary,
                "net_taxable_income": net_taxable_income,
                "initial_tax": initial_tax,
                "initial_marginal_rate": initial_marginal_rate,
                "recommended_per_amount": 0,
                "new_taxable_income": net_taxable_income,
                "new_tax": initial_tax,
                "tax_savings": 0,
                "message": f"Already at or below {target_tmi*100}% tax bracket"
            }
        
        # Calculate PER amount needed to reach target threshold
        recommended_per_amount = net_taxable_income - target_threshold
        new_taxable_income = net_taxable_income - recommended_per_amount
        new_tax = self.calculate_tax_on_income(new_taxable_income)
        tax_savings = initial_tax - new_tax
        
        return {
            "gross_salary": gross_salary,
            "abatement_amount": abatement_amount,
            "net_taxable_income": net_taxable_income,
            "initial_tax": initial_tax,
            "initial_marginal_rate": initial_marginal_rate,
            "recommended_per_amount": recommended_per_amount,
            "new_taxable_income": new_taxable_income,
            "new_tax": new_tax,
            "tax_savings": tax_savings,
            "savings_rate": tax_savings / recommended_per_amount if recommended_per_amount > 0 else 0,
            "target_tmi": target_tmi
        }
    
    def generate_tax_breakdown(self, taxable_income: float) -> List[Dict]:
        """
        Generate detailed tax breakdown by bracket.
        
        Args:
            taxable_income: Net taxable income in euros
            
        Returns:
            List of dictionaries with tax breakdown by bracket
        """
        breakdown = []
        
        for i, bracket in enumerate(self.TAX_BRACKETS_2024):
            if taxable_income <= bracket["min"]:
                break
                
            taxable_in_bracket = min(taxable_income, bracket["max"]) - bracket["min"]
            if taxable_in_bracket > 0:
                tax_in_bracket = taxable_in_bracket * bracket["rate"]
                breakdown.append({
                    "bracket": f"TMI {i}",
                    "range": f"{bracket['min']:,.0f}€ - {bracket['max']:,.0f}€" if bracket['max'] != float('inf') else f"{bracket['min']:,.0f}€+",
                    "rate": f"{bracket['rate']:.0%}",
                    "taxable_amount": taxable_in_bracket,
                    "tax_amount": tax_in_bracket
                })
        
        return breakdown
    
    def print_optimization_report(self, result: Dict) -> None:
        """
        Print a detailed optimization report.
        
        Args:
            result: Result dictionary from calculate_per_optimization
        """
        print("=" * 60)
        print("RAPPORT D'OPTIMISATION PER")
        print("=" * 60)
        
        print(f"\n📊 SITUATION INITIALE:")
        print(f"  Salaire brut annuel:        {result['gross_salary']:>10,.0f} €")
        if 'abatement_amount' in result:
            print(f"  Abattement (10%):           {result['abatement_amount']:>10,.0f} €")
        print(f"  Revenu net imposable:       {result['net_taxable_income']:>10,.0f} €")
        print(f"  Impôt initial:              {result['initial_tax']:>10,.0f} €")
        print(f"  TMI actuelle:               {result['initial_marginal_rate']:>10.0%}")
        
        if result['recommended_per_amount'] > 0:
            print(f"\n💰 OPTIMISATION PER:")
            print(f"  Versement PER recommandé:   {result['recommended_per_amount']:>10,.0f} €")
            print(f"  Nouveau revenu imposable:   {result['new_taxable_income']:>10,.0f} €")
            print(f"  Nouvel impôt:               {result['new_tax']:>10,.0f} €")
            print(f"  TMI cible:                  {result['target_tmi']:>10.0%}")
            
            print(f"\n🎯 ÉCONOMIES RÉALISÉES:")
            print(f"  Économie d'impôt:           {result['tax_savings']:>10,.0f} €")
            print(f"  Taux d'économie:            {result['savings_rate']:>10.1%}")
            print(f"  Réduction d'impôt:          {result['tax_savings']/result['initial_tax']:>10.1%}")
        else:
            print(f"\n✅ {result['message']}")

def main():
    """Main function to run PER optimization."""
    try:
        optimizer = PEROptimizer()
        
        # Get user input
        print("🔢 CALCULATEUR D'OPTIMISATION PER")
        print("-" * 40)
        
        while True:
            try:
                gross_salary = float(input("Entrez votre salaire brut annuel (€): "))
                if gross_salary > 0:
                    break
                print("Le salaire doit être positif.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Ask for target TMI
        print("\nTranches disponibles:")
        print("  0% (jusqu'à 11 294 €)")
        print("  11% (11 294 € - 28 797 €)")
        print("  30% (28 797 € - 82 341 €)")
        print("  41% (82 341 € - 177 106 €)")
        print("  45% (177 106 € et +)")
        
        while True:
            try:
                target_rate = float(input("\nTMI cible (en %, ex: 30): ")) / 100
                if target_rate in [0.0, 0.11, 0.30, 0.41, 0.45]:
                    break
                print("TMI non valide. Choisissez parmi: 0, 11, 30, 41, 45")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Calculate optimization
        result = optimizer.calculate_per_optimization(gross_salary, target_tmi=target_rate)
        
        # Print detailed report
        optimizer.print_optimization_report(result)
        
        # Show tax breakdown
        print(f"\n📋 DÉTAIL PAR TRANCHE (situation optimisée):")
        breakdown = optimizer.generate_tax_breakdown(result['new_taxable_income'])
        
        total_tax = 0
        for item in breakdown:
            print(f"  {item['bracket']} ({item['rate']:>3}): {item['taxable_amount']:>8,.0f} € → {item['tax_amount']:>6,.0f} €")
            total_tax += item['tax_amount']
        
        print(f"  {'TOTAL':>19}: {total_tax:>6,.0f} €")
        
    except KeyboardInterrupt:
        print("\n\nCalcul interrompu.")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
