"""Expérience 1 : distribution actuelle contre q*, sur la demande moyenne.

Responsable : M5, interprétation avec M6.
Dépend de : un solveur validé (Étape 9) et la baseline de M6 (Étape 11).

    Objectif    Mesurer le gain de la solution optimisée dans le cas le plus
                simple, sans aléa.
    Paramètres  D_i = µ_i (pas de tirage), µ de pénalisation à sa valeur de
                référence.
    Données     Le réseau synthétique complet.
    Méthode     Descente de gradient projetée, puis calcul de la distribution
                proportionnelle de référence sur le même scénario.
    Métriques   Coût total Σ c_e q_e², violation résiduelle ‖Aq − b‖,
                écart-type de satisfaction entre quartiers.
    Attendu     q* a un coût inférieur ou égal à la référence, avec une
                violation de contrainte proche de zéro.
    Graphique   Diagramme en barres comparant les deux stratégies par quartier.

Interprétation à porter dans le rapport : *pourquoi* la solution
proportionnelle n'est pas optimale au sens de Σ c_e q_e². L'intuition à
développer : le coût est quadratique en débit, donc concentrer un gros débit
sur une seule conduite coûte plus cher que le répartir sur deux, même si la
seconde a un coût unitaire supérieur. La stratégie proportionnelle ignore
complètement la topologie et les c_e ; c'est là que se loge le gain.

C'est cette expérience qui produit le livrable central du sujet. Si une seule
figure devait survivre dans le rapport, ce serait la sienne.
"""

from __future__ import annotations

import csv

import _bootstrap  # noqa: F401
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from data.generate_network import charger_reseau
from src.evaluation.baseline import distribution_proportionnelle
from src.evaluation.compare_strategies import comparer_sur_un_scenario
from src.evaluation.metrics import taux_de_satisfaction
from src.graph.build_graph import (
    construire_matrice_incidence,
    construire_second_membre,
    vecteur_couts,
)
from src.optimization.gradient_descent import descente_projetee
from src.probability.demand_model import parametres_demande

MU_PENALISATION = 100.0


def main() -> None:
    reseau = charger_reseau(_bootstrap.CONFIG)
    A = construire_matrice_incidence(reseau)
    demandes, _ = parametres_demande(reseau)
    b = construire_second_membre(reseau, demandes)
    q_optimal, historique = descente_projetee(
        A, b, vecteur_couts(reseau), MU_PENALISATION
    )
    q_reference = distribution_proportionnelle(reseau, demandes)
    comparaison = comparer_sur_un_scenario(reseau, A, demandes, q_optimal)

    with _bootstrap.TABLEAUX.joinpath("exp1_baseline_vs_optimal.csv").open(
        "w", newline="", encoding="utf-8"
    ) as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=comparaison.keys())
        ecrivain.writeheader()
        ecrivain.writerow(comparaison)

    quartiers = [quartier.identifiant for quartier in reseau.quartiers]
    plt.figure(figsize=(9, 5))
    plt.bar(np.arange(len(quartiers)) - 0.2,
            taux_de_satisfaction(reseau, q_reference, demandes), 0.4,
            label="Référence")
    plt.bar(np.arange(len(quartiers)) + 0.2,
            taux_de_satisfaction(reseau, q_optimal, demandes), 0.4,
            label="Optimisée")
    plt.xticks(np.arange(len(quartiers)), quartiers)
    plt.ylabel("Taux de satisfaction")
    plt.xlabel("Quartier")
    plt.legend()
    plt.tight_layout()
    plt.savefig(_bootstrap.FIGURES / "exp1_baseline_vs_optimal.png", dpi=180)
    plt.close()
    print(f"Expérience 1 terminée : coût référence={comparaison['cout_reference']:.2f}, "
          f"coût optimisé={comparaison['cout_optimise']:.2f}, "
          f"itérations={historique.n_iterations}")


if __name__ == "__main__":
    main()
