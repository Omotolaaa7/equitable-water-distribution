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

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M5, Expérience 1, bloquée par le jalon section 16.")


if __name__ == "__main__":
    main()
