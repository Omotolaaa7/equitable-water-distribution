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
    demandes = np.asarray(demandes, dtype=float)
    if demandes.shape != (len(reseau.quartiers),):
      raise ValueError(
        f"demandes doit être de longueur {len(reseau.quartiers)}, "
        f"reçu de forme {demandes.shape}."
      )
    if np.any(~np.isfinite(demandes)) or np.any(demandes < 0):
      raise ValueError("demandes doit contenir des valeurs finies positives ou nulles.")

    import networkx as nx

    graphe = nx.DiGraph()
    for conduite in reseau.conduites:
      graphe.add_edge(conduite.source, conduite.cible)

    index_conduite = {
      (conduite.source, conduite.cible): indice
      for indice, conduite in enumerate(reseau.conduites)
    }
    debits = np.zeros(len(reseau.conduites), dtype=float)

    for quartier, demande in zip(reseau.quartiers, demandes):
      candidats = []
      for reservoir in reseau.reservoirs:
        try:
          chemin = nx.shortest_path(graphe, reservoir.identifiant, quartier.identifiant)
        except nx.NetworkXNoPath:
          continue
        candidats.append((len(chemin), reservoir.identifiant, chemin))
      if not candidats:
        raise ValueError(f"Aucun chemin orienté vers le quartier {quartier.identifiant}.")

      _, _, chemin = min(candidats, key=lambda candidat: (candidat[0], candidat[1]))
      for source, cible in zip(chemin, chemin[1:]):
        debits[index_conduite[(source, cible)]] += demande

    return debits
