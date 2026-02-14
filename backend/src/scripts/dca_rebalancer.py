import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import json
import os
from pathlib import Path

# Charger les donnees des ETF depuis le fichier JSON
script_dir = Path(__file__).parent
data_file = script_dir.parent / "data" / "etfs.json"

with open(data_file, 'r', encoding='utf-8') as f:
    etfs_data = json.load(f)

# Recuperer les prix actuels via yfinance
print("Récupération des prix actuels des ETF...")
etf_prices = {}

for etf in etfs_data["etfs"]:
    ticker = etf["ticker"]
    try:
        # Methode plus robuste: creer un ticker individuel
        ticker_obj = yf.Ticker(ticker)
        
        # Essayer avec l'historique du dernier jour (plus fiable)
        hist = ticker_obj.history(period="1d")
        if not hist.empty and 'Close' in hist.columns:
            current_price = hist['Close'].iloc[-1]
            etf_prices[etf["name"]] = current_price
            print(f"  {etf['name']:15} ({ticker}): {current_price:.2f}€")
        else:
            raise ValueError("No price data available")
            
    except Exception as e:
        # Afficher l'erreur exacte pour debug
        print(f"  {etf['name']:15} ({ticker}): Erreur ({type(e).__name__}: {str(e)}), utilisation prix moyen {etf['averagePrice']:.2f}€")
        etf_prices[etf["name"]] = etf["averagePrice"]

print()

# Calculer la situation initiale basee sur le nombre de parts
invest_init = {}
for etf in etfs_data["etfs"]:
    invest_init[etf["name"]] = etf["shares"] * etf["averagePrice"]

# Ponderations cibles
target_alloc = {
    "MSCI World": 0.69,
    "S&P 500": 0.01,
    "Stoxx 50": 0.2,
    "Emerging Asia": 0.1,
}

# Parametres du DCA
dca_per_month = 8075.22
initial_cash = 0

# Frequences d'investissement depuis le JSON
investment_frequencies = {etf["name"]: etf["frequency"] for etf in etfs_data["etfs"]}

def calculate_monthly_allocation():
    """
    Calcule l'allocation optimale pour le mois suivant
    en fonction de la situation actuelle et de la cible
    """
    # Calculer la valeur actuelle du portefeuille
    current_amounts = {}
    for etf in etfs_data["etfs"]:
        current_amounts[etf["name"]] = etf["shares"] * etf_prices[etf["name"]]
    
    current_total = sum(current_amounts.values())
    
    print(f"\n{'='*70}")
    print("=== SITUATION ACTUELLE DU PORTEFEUILLE ===")
    print(f"Valeur totale: {current_total:.2f}€\n")
    
    # Afficher l'allocation actuelle vs cible
    print(f"{'ETF':<20} {'Valeur':<12} {'% Actuel':<12} {'% Cible':<12} {'Ecart':<10}")
    print("-" * 70)
    
    gaps = {}
    for asset in target_alloc:
        value = current_amounts[asset]
        current_pct = (value / current_total) * 100
        target_pct = target_alloc[asset] * 100
        gap_pct = current_pct - target_pct
        gaps[asset] = gap_pct
        
        status = "✓" if abs(gap_pct) <= 1.0 else ("↓" if gap_pct < 0 else "↑")
        print(f"{asset:<20} {value:>10.2f}€  {current_pct:>5.1f}%       {target_pct:>5.1f}%       {gap_pct:>+5.1f}%  {status}")
    
    # Calculer l'allocation optimale pour le budget du mois + cash restant
    total_budget = dca_per_month + initial_cash
    print(f"\n{'='*70}")
    print(f"=== ALLOCATION OPTIMALE CE MOIS ({dca_per_month}€ + {initial_cash:.2f}€ cash = {total_budget:.2f}€) ===\n")
    
    # Projeter le total apres investissement
    future_total = current_total + total_budget
    
    # Calculer combien il faudrait avoir par ETF
    target_amounts = {asset: future_total * pct for asset, pct in target_alloc.items()}
    
    # Calculer les montants necessaires pour chaque ETF
    needed_amounts = {asset: target_amounts[asset] - current_amounts[asset] for asset in target_alloc}
    
    # Algorithme optimise pour utiliser tout le budget disponible
    # Etape 1: Calculer l'allocation initiale basee sur les besoins
    positive_needs = {asset: max(0, amount) for asset, amount in needed_amounts.items()}
    total_positive_needs = sum(positive_needs.values())
    
    if total_positive_needs > 0:
        allocation_ratios = {asset: need / total_positive_needs for asset, need in positive_needs.items()}
    else:
        # Si tout est sur-alloue, repartir selon les cibles
        allocation_ratios = target_alloc.copy()
    
    # Etape 2: Calculer l'allocation initiale (actions entieres)
    monthly_allocation = {}
    remaining_budget = total_budget
    
    # D'abord allouer selon les ratios calcules
    for asset, freq in investment_frequencies.items():
        if freq == "mensuel":
            target_investment = total_budget * allocation_ratios[asset]
            shares_to_buy = int(target_investment / etf_prices[asset])  # Arrondir vers le bas
            actual_cost = shares_to_buy * etf_prices[asset]
            
            monthly_allocation[asset] = {
                "shares": shares_to_buy,
                "cost": actual_cost,
                "frequency": "mensuel",
                "priority": gaps[asset]  # Ecart negatif = sous-alloue = priorite haute
            }
            remaining_budget -= actual_cost
        
        elif freq == "trimestriel":
            # Pour le trimestriel, calculer le montant a mettre de cote
            target_investment = total_budget * allocation_ratios[asset]
            quarterly_target = target_investment * 3
            shares_to_buy = max(0, round(quarterly_target / etf_prices[asset]))
            actual_cost = shares_to_buy * etf_prices[asset]
            
            monthly_allocation[asset] = {
                "shares": shares_to_buy,
                "cost": actual_cost,
                "frequency": "trimestriel",
                "priority": gaps[asset]
            }
    
    # Etape 3: Utiliser le budget restant en achetant des actions supplementaires
    # Trier les actifs mensuels par priorite (les plus sous-alloues en premier)
    monthly_assets = [(asset, data) for asset, data in monthly_allocation.items() if data["frequency"] == "mensuel"]
    monthly_assets.sort(key=lambda x: x[1]["priority"])  # Tri croissant: ecart negatif = priorite
    
    while remaining_budget > 0:
        action_added = False
        
        for asset, data in monthly_assets:
            price = etf_prices[asset]
            if remaining_budget >= price:
                # Acheter une action supplementaire
                monthly_allocation[asset]["shares"] += 1
                monthly_allocation[asset]["cost"] += price
                remaining_budget -= price
                action_added = True
                break
        
        # Si aucune action n'a pu etre ajoutee, on arrete
        if not action_added:
            break
    
    # Affichage des resultats
    print(f"{'ETF':<20} {'A investir':<15} {'Actions':<10} {'Cout reel':<12}")
    print("-" * 70)
    
    total_spent = 0
    for asset, freq in investment_frequencies.items():
        alloc = monthly_allocation[asset]
        if freq == "mensuel":
            print(f"{asset:<20} {total_budget * allocation_ratios[asset]:>10.2f}€    {alloc['shares']:>3} part(s)  {alloc['cost']:>10.2f}€")
            total_spent += alloc['cost']
        elif freq == "trimestriel":
            print(f"{asset:<20} {total_budget * allocation_ratios[asset]:>10.2f}€/mois (trimestriel: {alloc['shares']} part(s) = {alloc['cost']:.2f}€)")
    
    print("-" * 70)
    print(f"{'TOTAL CE MOIS':<35} {total_spent:>10.2f}€")
    print(f"{'Cash restant pour le mois prochain':<35} {remaining_budget:>10.2f}€")
    
    # Simuler l'allocation apres investissement
    print(f"\n{'='*70}")
    print("=== PROJECTION APRES INVESTISSEMENT ===\n")
    
    future_amounts = current_amounts.copy()
    for asset, alloc in monthly_allocation.items():
        if alloc["frequency"] == "mensuel":
            future_amounts[asset] += alloc["cost"]
    
    future_total_actual = sum(future_amounts.values())
    
    print(f"{'ETF':<20} {'Nouvelle valeur':<15} {'% Futur':<12} {'% Cible':<12} {'Ecart':<10}")
    print("-" * 70)
    
    for asset in target_alloc:
        value = future_amounts[asset]
        future_pct = (value / future_total_actual) * 100
        target_pct = target_alloc[asset] * 100
        gap_pct = future_pct - target_pct
        
        status = "✓" if abs(gap_pct) <= 1.0 else ("↓" if gap_pct < 0 else "↑")
        print(f"{asset:<20} {value:>12.2f}€  {future_pct:>5.1f}%       {target_pct:>5.1f}%       {gap_pct:>+5.1f}%  {status}")
    
    print(f"\nValeur totale projetee: {future_total_actual:.2f}€")
    
    return monthly_allocation

# Executer le calcul
monthly_plan = calculate_monthly_allocation()

# Instructions finales
print(f"\n{'='*70}")
print("=== INSTRUCTIONS POUR VOTRE BROKER ===\n")

for asset, alloc in monthly_plan.items():
    if alloc["frequency"] == "mensuel" and alloc["shares"] > 0:
        print(f"  • {asset}: Acheter {alloc['shares']} part(s) ce mois ({alloc['cost']:.2f}€)")
    elif alloc["frequency"] == "trimestriel":
        print(f"  • {asset}: Mettre de cote pour achat trimestriel ({alloc['shares']} part(s) = {alloc['cost']:.2f}€)")

print(f"\n{'='*70}")