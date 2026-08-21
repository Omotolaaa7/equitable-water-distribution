"""Expérience 2 — Robustesse sur plusieurs scénarios Monte-Carlo.

Responsable : M5, interprétation avec M3 et M6.
Dépend de : le modèle de demande figé (Étape 4) et un solveur validé.

    Objectif    Évaluer la stabilité des deux stratégies face à l'incertitude.
    Paramètres  N tirages de D_i ~ N(µ_i, σ_i²) — N = 1000 en référence.
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
d'estimation décroît bien en 1/√N — c'est la vérification empirique du
résultat théorique de l'Étape 5.

Le résultat le plus intéressant n'est pas forcément que q* coûte moins cher,
mais qu'il *varie moins*. Pour un réseau d'eau, la variance est un argument au
moins aussi fort que la moyenne : c'est la défaillance ponctuelle qui coûte.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M5 — Expérience 2.")


if __name__ == "__main__":
    main()
