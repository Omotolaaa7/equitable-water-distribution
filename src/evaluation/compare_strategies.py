"""Comparaison chiffrée entre distribution actuelle et distribution optimisée.

Responsable : M6, en collaboration avec M5.
Dépend de : ``baseline``, ``metrics`` et les résultats de M5.
Étapes 11 et 12 du pipeline.

C'est le livrable explicite du sujet :

    « Une comparaison chiffrée entre la distribution actuelle du réseau
      (proportionnelle aux demandes) et la distribution optimisée q*, testée
      sur plusieurs scénarios de demande simulés. »

« Plusieurs scénarios » n'est pas négociable : la section 10.5 du plan précise
que ce livrable n'est terminé que si le tableau chiffré existe pour plusieurs
scénarios, et pas uniquement pour la demande moyenne.
"""

from __future__ import annotations

import numpy as np


def comparer_sur_un_scenario(reseau, A: np.ndarray, demandes: np.ndarray, q_optimal: np.ndarray) -> dict:
    """Compare référence et q* sur un scénario, toutes métriques confondues.

    Returns:
        Un dictionnaire à plat, prêt à devenir une ligne de DataFrame.
    """
    raise NotImplementedError("M6 — Étape 11.")


def comparer_sur_scenarios(reseau, A: np.ndarray, resultats) -> "object":
    """Agrège la comparaison sur l'ensemble des scénarios Monte-Carlo.

    Ce que le tableau final doit porter, en plus des moyennes : la *dispersion*
    de chaque métrique sur les scénarios. Une stratégie légèrement plus chère en
    moyenne mais nettement plus stable peut être préférable pour un réseau
    d'eau, où c'est la défaillance ponctuelle qui coûte. Réduire la comparaison
    à deux moyennes ferait disparaître cet argument, qui est l'un des plus forts
    en faveur de q*.

    Returns:
        Un ``pandas.DataFrame``, une ligne par scénario.
    """
    raise NotImplementedError("M6 — Étape 11.")


def synthese(comparaison) -> "object":
    """Construit le tableau de synthèse destiné au rapport.

    Une ligne par métrique, une colonne par stratégie, plus l'écart relatif.
    C'est ce tableau qui est cité dans la section « Analyse des résultats ».

    Returns:
        Un ``pandas.DataFrame`` prêt à exporter dans ``results/tables/``.
    """
    raise NotImplementedError("M6 — Étape 11.")


def test_significativite(couts_reference: np.ndarray, couts_optimise: np.ndarray) -> dict:
    """Teste si l'écart de coût entre les deux stratégies est statistiquement réel.

    Sans ce test, la comparaison reste descriptive : « q* coûte moins cher sur
    nos tirages » ne dit pas si l'écart survit à l'incertitude de simulation.

    Choix à justifier dans le rapport : les deux stratégies sont évaluées **sur
    les mêmes scénarios**, donc les échantillons sont appariés. Un test apparié
    est plus puissant qu'un test à deux échantillons indépendants, et appliquer
    ce dernier ici serait une erreur de méthode — pas seulement un choix
    sous-optimal.

    Returns:
        Statistique de test, p-valeur, et taille d'effet.
    """
    raise NotImplementedError("M6 — Étape 12, volet statistique de la validation.")
