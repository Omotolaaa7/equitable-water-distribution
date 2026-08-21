"""Expérience 5 — Effet du maillage du réseau sur le conditionnement.

Responsable : M5, interprétation avec M2.
Dépend de : ``generer_variantes_de_maillage`` (M1/M2) et l'analyse de l'Étape 3.

Seconde confrontation théorie/expérience exigée par le sujet. Elle valide
l'affirmation centrale du volet algèbre linéaire : un réseau mal maillé se
traduit directement par une instabilité numérique de la résolution.

    Objectif    Vérifier empiriquement le lien entre structure du graphe et
                stabilité numérique établi à l'Étape 3.
    Paramètres  Plusieurs variantes du réseau, de l'arbre couvrant au réseau
                bien maillé.
    Données     Réseaux synthétiques à densités de connexion différentes.
    Méthode     Calculer κ pour chaque variante, résoudre et compter les
                itérations nécessaires.
    Métriques   Conditionnement, nombre d'itérations à convergence.
    Attendu     Un réseau mal maillé a un conditionnement plus élevé et
                nécessite davantage d'itérations.
    Graphique   Conditionnement en fonction du nombre de conduites, ou
                itérations en fonction du conditionnement.

Conditions de validité du protocole, à tenir sous peine de comparer des choses
différentes :

- toutes les variantes doivent rester connexes, sinon le rang de A change de
  nature et les κ ne sont plus comparables ;
- µ, η et la tolérance doivent être identiques d'une variante à l'autre ;
- si η est dérivé de 2/L, il change *mécaniquement* avec le conditionnement.
  Deux protocoles se défendent — η fixe pour tous, ou η adapté à chaque
  variante — mais ils ne mesurent pas la même chose, et le rapport doit dire
  lequel est retenu et pourquoi.

Le résultat attendu est une relation croissante, pas une droite : ne pas
sur-interpréter une régression linéaire sur cinq points.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M5 avec M2 — Expérience 5.")


if __name__ == "__main__":
    main()
