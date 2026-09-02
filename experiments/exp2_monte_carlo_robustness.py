"""Expérience 2 : robustesse sur plusieurs scénarios Monte-Carlo.

Responsable : M5, interprétation avec M3 et M6.
Dépend de : le modèle de demande figé (Étape 4) et un solveur validé.

    Objectif    Évaluer la stabilité des deux stratégies face à l'incertitude.
    Paramètres  N tirages de D_i ~ N(µ_i, σ_i²), avec N = 1000 en référence.
    Données     Mêmes réseau et lois qu'à l'Expérience 1.
    Méthode     Résoudre le problème pour chaque scénario, agréger.
    Métriques   Moyenne et variance du coût total sur les scénarios, taux de
                scénarios où la contrainte est bien respectée.
    Attendu     q* reste globalement meilleur ou plus stable que la référence
                sur l'ensemble des scénarios.
    Graphique   Histogramme de la distribution des coûts, deux stratégies
                superposées.

Interprétation : lien avec la loi des grands nombres et la fiabilité
statistique de la comparaison. Reprendre ici les tailles croissantes de
``convergence_par_taille`` (100, 1 000, 10 000) pour montrer que l'erreur
d'estimation décroît bien en 1/√N. C'est la vérification empirique du
résultat théorique de l'Étape 5.

Le résultat le plus intéressant n'est pas forcément que q* coûte moins cher,
mais qu'il *varie moins*. Pour un réseau d'eau, la variance est un argument au
moins aussi fort que la moyenne : c'est la défaillance ponctuelle qui coûte.
"""

from __future__ import annotations

import matplotlib

import _bootstrap  # noqa: F401
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from data.generate_network import charger_reseau
from src.evaluation.compare_strategies import (
    comparer_sur_scenarios,
    synthese,
    test_significativite,
)
from src.graph.build_graph import construire_matrice_incidence
from src.probability.monte_carlo import generer_scenarios
from src.simulation.run_scenarios import resoudre_tous


def main() -> None:
    reseau = charger_reseau(_bootstrap.CONFIG)
    A = construire_matrice_incidence(reseau)
    scenarios = generer_scenarios(reseau, n_tirages=1000, graine=42)
    resultats = resoudre_tous(reseau, A, scenarios, mu=100.0)
    comparaison = comparer_sur_scenarios(reseau, A, resultats)
    resume = synthese(comparaison)

    comparaison.to_csv(_bootstrap.TABLEAUX / "exp2_comparaison_scenarios.csv", index=False)
    resume.to_csv(_bootstrap.TABLEAUX / "exp2_synthese.csv", index=False)
    test = test_significativite(
        comparaison["cout_reference"].to_numpy(),
        comparaison["cout_optimise"].to_numpy(),
    )
    with _bootstrap.TABLEAUX.joinpath("exp2_test_significativite.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fichier:
        ecrivain = __import__("csv").DictWriter(fichier, fieldnames=test.keys())
        ecrivain.writeheader()
        ecrivain.writerow(test)

    plt.figure(figsize=(9, 5))
    plt.hist(comparaison["cout_reference"], bins=30, alpha=0.55, label="Référence")
    plt.hist(comparaison["cout_optimise"], bins=30, alpha=0.55, label="Optimisée")
    plt.xlabel("Coût technique")
    plt.ylabel("Nombre de scénarios")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_bootstrap.FIGURES / "exp2_monte_carlo_robustness.png", dpi=180)
    plt.close()
    print(f"Expérience 2 terminée : {len(comparaison)} scénarios, "
          f"différence moyenne={test['difference_moyenne']:.2f}, "
          f"p-valeur={test['p_valeur']:.3g}")


if __name__ == "__main__":
    main()
