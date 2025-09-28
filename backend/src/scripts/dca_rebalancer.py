import pandas as pd
import matplotlib.pyplot as plt

# Paramètres initiaux
invest_init = {
    "MSCI World": 0,
    "S&P 500": 1685,
    "Stoxx 50": 0,
    "Emerging Asia": 255,
}

# Pondérations cibles
target_alloc = {
    "MSCI World": 0.60,
    "S&P 500": 0.20,
    "Stoxx 50": 0.15,
    "Emerging Asia": 0.05,
}

# Paramètres du DCA
dca_per_month = 500
initial_cash = 2820  # Liquidité immédiate disponible le premier mois
nb_months = 12

# DataFrame pour stocker les résultats
df = pd.DataFrame(columns=["Mois"] + list(invest_init.keys()))

# État actuel du portefeuille
current_alloc = invest_init.copy()

for month in range(1, nb_months + 1):
    # Montant à investir ce mois : liquidité immédiate au 1er mois, puis DCA mensuel
    if month == 1:
        monthly_investment = initial_cash
    else:
        monthly_investment = dca_per_month
    
    # Montant total après ajout de l'investissement du mois
    total_after_investment = sum(current_alloc.values()) + monthly_investment

    # Cible en € après investissement
    target_values = {k: total_after_investment * v for k, v in target_alloc.items()}

    # Calculer les écarts (positifs = sous-alloué, négatifs = sur-alloué)
    gaps = {k: target_values[k] - current_alloc[k] for k in current_alloc}
    
    # Répartir l'investissement uniquement sur les actifs sous-alloués
    positive_gaps = {k: v for k, v in gaps.items() if v > 0}
    total_positive_gaps = sum(positive_gaps.values())
    
    # Si il y a des écarts positifs, répartir l'investissement proportionnellement
    if total_positive_gaps > 0:
        for k in current_alloc:
            if k in positive_gaps:
                proportion = positive_gaps[k] / total_positive_gaps
                current_alloc[k] += monthly_investment * proportion
    else:
        # Si pas d'écarts positifs, répartir selon les cibles
        for k in current_alloc:
            current_alloc[k] += monthly_investment * target_alloc[k]

    # Stocker l’état du mois
    row = {"Mois": month}
    row.update(current_alloc)
    df.loc[len(df)] = row

# Affichage du tableau
print(df)

# Graphique
for col in invest_init.keys():
    plt.plot(df["Mois"], df[col], label=col)

plt.title("Évolution du portefeuille (simulation DCA)")
plt.xlabel("Mois")
plt.ylabel("Montant investi (€)")
plt.legend()
plt.grid(True)
plt.show()
