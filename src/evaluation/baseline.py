"""Stratégie de référence : la distribution actuelle du réseau.

Responsable : M6.
Dépend de : la définition figée dans ``data/network_config.json``.
Étape 11 du pipeline.

Le sujet impose une comparaison à une stratégie de référence, et cette
référence est la pratique actuelle de la société : une répartition
proportionnelle à la demande moyenne, décidée sans considération du coût des
conduites empruntées.

Deux exigences croisées à tenir :

- La référence doit être *honnête*. Une baseline artificiellement mauvaise
  rendrait la comparaison finale sans valeur, et un correcteur le verra.
- Elle doit être définie avec la même précision que q*, faute de quoi les deux
  chiffres du tableau final ne sont pas comparables.
"""

from __future__ import annotations

import numpy as np


def distribution_proportionnelle(reseau, demandes: np.ndarray) -> np.ndarray:
    """Calcule les débits de la stratégie actuelle.

    Chaque quartier reçoit une part de l'offre proportionnelle à sa demande.
    Reste à traduire cette règle, qui porte sur les *quartiers*, en débits sur
    les *conduites*, car c'est sur les conduites que se mesure le coût
    Σ c_e q_e², et donc le seul niveau où la comparaison avec q* a un sens.

    Ce passage n'est pas unique dès que le réseau contient des cycles :
    plusieurs répartitions de débits acheminent la même quantité à chaque
    quartier. La règle de désambiguïsation retenue (répartition uniforme entre
    les chemins, ou par plus court chemin depuis le réservoir le plus proche)
    est une décision de modélisation qui doit être écrite et défendue dans le
    rapport, pas tranchée en silence dans le code. C'est précisément parce que
    ce choix existe qu'il y a quelque chose à optimiser.

    Args:
        reseau: le ``Reseau``.
        demandes: vecteur des D_i pour le scénario considéré.

    Returns:
        Les débits de référence, longueur |E|, comparables à q*.
    """
    raise NotImplementedError(
        "M6, Étape 11. Fixer et documenter la règle de passage quartiers → conduites."
    )
