"""
PER (Plan d'Épargne Retraite) Optimizer Script

This script calculates the optimal amount to invest in a PER based on salary
and tax optimization, following French tax brackets for 2024.
Supports actual expenses, tax shares (parts fiscales), and detailed calculations.
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
import pandas as pd

# Add the parent directory to import AssetManager if needed
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)
sys.path.insert(0, src_dir)

class PEROptimizer:
    """
    Calculates optimal PER investment based on French tax brackets and salary.
    Supports tax shares (parts fiscales) and actual vs. standard deductions.
    """
    
    # French tax brackets for 2024 (per tax share)
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
    
    def calculate_tax_on_income(self, taxable_income_per_share: float) -> float:
        """
        Calculate income tax based on French tax brackets per tax share.
        
        Args:
            taxable_income_per_share: Net taxable income per tax share in euros
            
        Returns:
            Total tax amount per tax share in euros
        """
        total_tax = 0.0
        
        for bracket in self.TAX_BRACKETS_2024:
            if taxable_income_per_share <= bracket["min"]:
                break
                
            taxable_in_bracket = min(taxable_income_per_share, bracket["max"]) - bracket["min"]
            if taxable_in_bracket > 0:
                total_tax += taxable_in_bracket * bracket["rate"]
        
        return total_tax
    
    def get_marginal_tax_rate(self, taxable_income_per_share: float) -> float:
        """
        Get the marginal tax rate for a given income per tax share.
        
        Args:
            taxable_income_per_share: Net taxable income per tax share in euros
            
        Returns:
            Marginal tax rate as a decimal (e.g., 0.30 for 30%)
        """
        for bracket in self.TAX_BRACKETS_2024:
            if bracket["min"] <= taxable_income_per_share <= bracket["max"]:
                return bracket["rate"]
        return 0.0
    
    def calculate_deductions(self, gross_salary: float, 
                           use_actual_expenses: bool = False,
                           actual_expenses: float = 0) -> Tuple[float, str]:
        """
        Calculate professional deductions (standard 10% or actual expenses).
        
        Args:
            gross_salary: Annual gross salary in euros
            use_actual_expenses: Whether to use actual expenses instead of 10% deduction
            actual_expenses: Amount of actual professional expenses
            
        Returns:
            Tuple of (deduction_amount, deduction_type)
        """
        standard_deduction = gross_salary * 0.10
        # Standard deduction is capped at 12,829€ for 2024
        standard_deduction = min(standard_deduction, 12829)
        
        if use_actual_expenses:
            return actual_expenses, f"Frais réels: {actual_expenses:,.0f} €"
        else:
            return standard_deduction, f"Abattement forfaitaire (10%): {standard_deduction:,.0f} €"
    
    def calculate_per_optimization(self, gross_salary: float,
                                 tax_shares: float = 1.0,
                                 use_actual_expenses: bool = False,
                                 actual_expenses: float = 0,
                                 target_tmi: float = 0.30,
                                 custom_per_amount: Optional[float] = None) -> Dict:
        """
        Calculate optimal PER investment to reach a target tax bracket.
        
        Args:
            gross_salary: Annual gross salary in euros
            tax_shares: Number of tax shares (parts fiscales)
            use_actual_expenses: Whether to use actual expenses
            actual_expenses: Amount of actual professional expenses
            target_tmi: Target marginal tax rate to reach (default 30%)
            custom_per_amount: Custom PER amount to test (optional)
            
        Returns:
            Dictionary with optimization results
        """
        # Calculate deductions
        deduction_amount, deduction_desc = self.calculate_deductions(
            gross_salary, use_actual_expenses, actual_expenses
        )
        
        # Calculate net taxable income
        net_taxable_income = gross_salary - deduction_amount
        net_taxable_income_per_share = net_taxable_income / tax_shares
        
        # Calculate initial tax
        initial_tax_per_share = self.calculate_tax_on_income(net_taxable_income_per_share)
        initial_tax_total = initial_tax_per_share * tax_shares
        initial_marginal_rate = self.get_marginal_tax_rate(net_taxable_income_per_share)
        
        if custom_per_amount is not None:
            # Test custom PER amount
            recommended_per_amount = custom_per_amount
            new_taxable_income = net_taxable_income - recommended_per_amount
            new_taxable_income_per_share = new_taxable_income / tax_shares
            new_tax_per_share = self.calculate_tax_on_income(new_taxable_income_per_share)
            new_tax_total = new_tax_per_share * tax_shares
            tax_savings = initial_tax_total - new_tax_total
            new_marginal_rate = self.get_marginal_tax_rate(new_taxable_income_per_share)
            
            return {
                "gross_salary": gross_salary,
                "tax_shares": tax_shares,
                "deduction_amount": deduction_amount,
                "deduction_desc": deduction_desc,
                "net_taxable_income": net_taxable_income,
                "net_taxable_income_per_share": net_taxable_income_per_share,
                "initial_tax": initial_tax_total,
                "initial_marginal_rate": initial_marginal_rate,
                "recommended_per_amount": recommended_per_amount,
                "new_taxable_income": new_taxable_income,
                "new_taxable_income_per_share": new_taxable_income_per_share,
                "new_tax": new_tax_total,
                "new_marginal_rate": new_marginal_rate,
                "tax_savings": tax_savings,
                "savings_rate": tax_savings / recommended_per_amount if recommended_per_amount > 0 else 0,
                "target_tmi": target_tmi,
                "is_custom_amount": True
            }
        
        # Find the threshold for target TMI
        target_threshold = None
        for bracket in self.TAX_BRACKETS_2024:
            if bracket["rate"] == target_tmi:
                target_threshold = bracket["max"]
                break
        
        if target_threshold is None or net_taxable_income_per_share <= target_threshold:
            return {
                "gross_salary": gross_salary,
                "tax_shares": tax_shares,
                "deduction_amount": deduction_amount,
                "deduction_desc": deduction_desc,
                "net_taxable_income": net_taxable_income,
                "net_taxable_income_per_share": net_taxable_income_per_share,
                "initial_tax": initial_tax_total,
                "initial_marginal_rate": initial_marginal_rate,
                "recommended_per_amount": 0,
                "new_taxable_income": net_taxable_income,
                "new_taxable_income_per_share": net_taxable_income_per_share,
                "new_tax": initial_tax_total,
                "new_marginal_rate": initial_marginal_rate,
                "tax_savings": 0,
                "target_tmi": target_tmi,
                "message": f"Déjà dans la tranche {target_tmi*100:.0f}% ou inférieure",
                "is_custom_amount": False
            }
        
        # Calculate PER amount needed to reach target threshold per share
        recommended_per_amount = (net_taxable_income_per_share - target_threshold) * tax_shares
        new_taxable_income = net_taxable_income - recommended_per_amount
        new_taxable_income_per_share = new_taxable_income / tax_shares
        new_tax_per_share = self.calculate_tax_on_income(new_taxable_income_per_share)
        new_tax_total = new_tax_per_share * tax_shares
        tax_savings = initial_tax_total - new_tax_total
        
        return {
            "gross_salary": gross_salary,
            "tax_shares": tax_shares,
            "deduction_amount": deduction_amount,
            "deduction_desc": deduction_desc,
            "net_taxable_income": net_taxable_income,
            "net_taxable_income_per_share": net_taxable_income_per_share,
            "initial_tax": initial_tax_total,
            "initial_marginal_rate": initial_marginal_rate,
            "recommended_per_amount": recommended_per_amount,
            "new_taxable_income": new_taxable_income,
            "new_taxable_income_per_share": new_taxable_income_per_share,
            "new_tax": new_tax_total,
            "new_marginal_rate": self.get_marginal_tax_rate(new_taxable_income_per_share),
            "tax_savings": tax_savings,
            "savings_rate": tax_savings / recommended_per_amount if recommended_per_amount > 0 else 0,
            "target_tmi": target_tmi,
            "is_custom_amount": False
        }
    
    def generate_tax_breakdown(self, taxable_income_per_share: float, tax_shares: float) -> List[Dict]:
        """
        Generate detailed tax breakdown by bracket.
        
        Args:
            taxable_income_per_share: Net taxable income per tax share in euros
            tax_shares: Number of tax shares
            
        Returns:
            List of dictionaries with tax breakdown by bracket
        """
        breakdown = []
        
        for i, bracket in enumerate(self.TAX_BRACKETS_2024):
            if taxable_income_per_share <= bracket["min"]:
                break
                
            taxable_in_bracket = min(taxable_income_per_share, bracket["max"]) - bracket["min"]
            if taxable_in_bracket > 0:
                tax_in_bracket_per_share = taxable_in_bracket * bracket["rate"]
                tax_in_bracket_total = tax_in_bracket_per_share * tax_shares
                breakdown.append({
                    "bracket": f"TMI {i}",
                    "range": f"{bracket['min']:,.0f}€ - {bracket['max']:,.0f}€" if bracket['max'] != float('inf') else f"{bracket['min']:,.0f}€+",
                    "rate": f"{bracket['rate']:.0%}",
                    "taxable_amount_per_share": taxable_in_bracket,
                    "taxable_amount_total": taxable_in_bracket * tax_shares,
                    "tax_amount_per_share": tax_in_bracket_per_share,
                    "tax_amount_total": tax_in_bracket_total
                })
        
        return breakdown
    
    def print_optimization_report(self, result: Dict) -> None:
        """
        Print a detailed optimization report.
        
        Args:
            result: Result dictionary from calculate_per_optimization
        """
        print("=" * 70)
        print("RAPPORT D'OPTIMISATION PER")
        print("=" * 70)
        
        print(f"\n📊 SITUATION INITIALE:")
        print(f"  Salaire brut annuel:              {result['gross_salary']:>12,.0f} €")
        print(f"  {result['deduction_desc']}")
        print(f"  Nombre de parts fiscales:         {result['tax_shares']:>12.1f}")
        print(f"  Revenu net imposable total:       {result['net_taxable_income']:>12,.0f} €")
        print(f"  Revenu net imposable par part:    {result['net_taxable_income_per_share']:>12,.0f} €")
        print(f"  Impôt initial:                    {result['initial_tax']:>12,.0f} €")
        print(f"  TMI actuelle:                     {result['initial_marginal_rate']:>12.0%}")
        
        if result['recommended_per_amount'] > 0:
            action_type = "MONTANT TESTÉ:" if result.get('is_custom_amount') else "OPTIMISATION PER:"
            print(f"\n💰 {action_type}")
            print(f"  Versement PER:                    {result['recommended_per_amount']:>12,.0f} €")
            print(f"  Nouveau revenu imposable total:   {result['new_taxable_income']:>12,.0f} €")
            print(f"  Nouveau revenu imposable/part:    {result['new_taxable_income_per_share']:>12,.0f} €")
            print(f"  Nouvel impôt:                     {result['new_tax']:>12,.0f} €")
            print(f"  Nouvelle TMI:                     {result['new_marginal_rate']:>12.0%}")
            
            if not result.get('is_custom_amount'):
                print(f"  TMI cible atteinte:               {result['target_tmi']:>12.0%}")
            
            print(f"\n🎯 ÉCONOMIES RÉALISÉES:")
            print(f"  Économie d'impôt:                 {result['tax_savings']:>12,.0f} €")
            print(f"  Taux d'économie:                  {result['savings_rate']:>12.1%}")
            if result['initial_tax'] > 0:
                print(f"  Réduction d'impôt relative:       {result['tax_savings']/result['initial_tax']:>12.1%}")
        else:
            print(f"\n✅ {result.get('message', 'Aucune optimisation nécessaire')}")

def main():
    """Main function to run PER optimization."""
    try:
        optimizer = PEROptimizer()
        
        # Get user input
        print("🔢 CALCULATEUR D'OPTIMISATION PER")
        print("Note: Calculs basés sur les barèmes 2024")
        print("-" * 50)
        
        # Salary input
        while True:
            try:
                gross_salary = float(input("Entrez votre salaire brut annuel (€): "))
                if gross_salary > 0:
                    break
                print("Le salaire doit être positif.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Tax shares input
        while True:
            try:
                tax_shares = float(input("Nombre de parts fiscales (ex: 1, 1.5, 2): "))
                if tax_shares > 0:
                    break
                print("Le nombre de parts doit être positif.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Deduction type
        print("\nType de déduction:")
        print("  1. Abattement forfaitaire de 10% (plafonné à 12 829 €)")
        print("  2. Frais réels")
        
        use_actual_expenses = False
        actual_expenses = 0
        while True:
            choice = input("Votre choix (1 ou 2): ").strip()
            if choice == "1":
                break
            elif choice == "2":
                use_actual_expenses = True
                while True:
                    try:
                        actual_expenses = float(input("Montant des frais réels (€): "))
                        if actual_expenses >= 0:
                            break
                        print("Les frais réels doivent être positifs ou nuls.")
                    except ValueError:
                        print("Veuillez entrer un nombre valide.")
                break
            else:
                print("Veuillez choisir 1 ou 2.")
        
        # Calculation mode
        print("\nMode de calcul:")
        print("  1. Optimisation automatique vers une TMI cible")
        print("  2. Test d'un montant PER spécifique")
        
        while True:
            mode = input("Votre choix (1 ou 2): ").strip()
            if mode in ["1", "2"]:
                break
            print("Veuillez choisir 1 ou 2.")
        
        if mode == "1":
            # Target TMI mode
            print("\nTranches marginales disponibles:")
            print("  0% (jusqu'à 11 294 € par part)")
            print("  11% (11 294 € - 28 797 € par part)")
            print("  30% (28 797 € - 82 341 € par part)")
            print("  41% (82 341 € - 177 106 € par part)")
            print("  45% (177 106 € et + par part)")
            
            while True:
                try:
                    target_rate = float(input("\nTMI cible (en %, ex: 30): ")) / 100
                    if target_rate in [0.0, 0.11, 0.30, 0.41, 0.45]:
                        break
                    print("TMI non valide. Choisissez parmi: 0, 11, 30, 41, 45")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")
            
            result = optimizer.calculate_per_optimization(
                gross_salary, tax_shares, use_actual_expenses, 
                actual_expenses, target_tmi=target_rate
            )
        else:
            # Custom PER amount mode
            while True:
                try:
                    custom_amount = float(input("\nMontant PER à tester (€): "))
                    if custom_amount >= 0:
                        break
                    print("Le montant doit être positif ou nul.")
                except ValueError:
                    print("Veuillez entrer un nombre valide.")
            
            result = optimizer.calculate_per_optimization(
                gross_salary, tax_shares, use_actual_expenses, 
                actual_expenses, custom_per_amount=custom_amount
            )
        
        # Print detailed report
        optimizer.print_optimization_report(result)
        
        # Show tax breakdown
        print(f"\n📋 DÉTAIL PAR TRANCHE (situation après PER):")
        breakdown = optimizer.generate_tax_breakdown(
            result['new_taxable_income_per_share'], 
            result['tax_shares']
        )
        
        total_tax = 0
        for item in breakdown:
            if result['tax_shares'] == 1.0:
                print(f"  {item['bracket']} ({item['rate']:>3}): "
                      f"{item['taxable_amount_per_share']:>8,.0f} € → "
                      f"{item['tax_amount_per_share']:>6,.0f} €")
            else:
                print(f"  {item['bracket']} ({item['rate']:>3}): "
                      f"{item['taxable_amount_per_share']:>8,.0f} € × {result['tax_shares']:.1f} = "
                      f"{item['taxable_amount_total']:>8,.0f} € → "
                      f"{item['tax_amount_total']:>6,.0f} €")
            total_tax += item['tax_amount_total']
        
        print(f"  {'TOTAL':>25}: {total_tax:>6,.0f} €")
        
        # Show PER amount to invest
        if result['recommended_per_amount'] > 0:
            print(f"\n💡 MONTANT À VERSER SUR LE PER: {result['recommended_per_amount']:,.0f} €")
        
    except KeyboardInterrupt:
        print("\n\nCalcul interrompu.")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
