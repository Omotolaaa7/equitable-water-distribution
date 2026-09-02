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

from src.evaluation.baseline import distribution_proportionnelle
from src.evaluation.metrics import (
    cout_total,
    ecart_type_satisfaction,
    quartier_le_moins_servi,
    taux_de_satisfaction,
    violation_conservation,
)
from src.graph.build_graph import construire_second_membre, vecteur_couts


def comparer_sur_un_scenario(reseau, A: np.ndarray, demandes: np.ndarray, q_optimal: np.ndarray) -> dict:
    """Compare référence et q* sur un scénario, toutes métriques confondues.

    Returns:
        Un dictionnaire à plat, prêt à devenir une ligne de DataFrame.
    """
    demandes = np.asarray(demandes, dtype=float)
    q_optimal = np.asarray(q_optimal, dtype=float)
    q_reference = distribution_proportionnelle(reseau, demandes)
    b = construire_second_membre(reseau, demandes)
    couts = vecteur_couts(reseau)
    taux_reference = taux_de_satisfaction(reseau, q_reference, demandes)
    taux_optimal = taux_de_satisfaction(reseau, q_optimal, demandes)
    quartier_reference, minimum_reference = quartier_le_moins_servi(reseau, taux_reference)
    quartier_optimal, minimum_optimal = quartier_le_moins_servi(reseau, taux_optimal)
    return {
        "cout_reference": cout_total(q_reference, couts),
        "cout_optimise": cout_total(q_optimal, couts),
        "violation_reference": violation_conservation(q_reference, A, b),
        "violation_optimise": violation_conservation(q_optimal, A, b),
        "satisfaction_moyenne_reference": float(np.mean(taux_reference)),
        "satisfaction_moyenne_optimise": float(np.mean(taux_optimal)),
        "ecart_type_reference": ecart_type_satisfaction(taux_reference),
        "ecart_type_optimise": ecart_type_satisfaction(taux_optimal),
        "quartier_moins_servi_reference": quartier_reference,
        "quartier_moins_servi_optimise": quartier_optimal,
        "minimum_satisfaction_reference": minimum_reference,
        "minimum_satisfaction_optimise": minimum_optimal,
    }


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
    import pandas as pd

    lignes = []
    for resultat in resultats:
        ligne = comparer_sur_un_scenario(
            reseau, A, resultat.demandes, resultat.q_optimal
        )
        ligne["indice"] = resultat.indice
        ligne["a_converge"] = resultat.a_converge
        ligne["n_iterations"] = resultat.n_iterations
        lignes.append(ligne)
    return pd.DataFrame(lignes)


def synthese(comparaison) -> "object":
    """Construit le tableau de synthèse destiné au rapport.

    Une ligne par métrique, une colonne par stratégie, plus l'écart relatif.
    C'est ce tableau qui est cité dans la section « Analyse des résultats ».

    Returns:
        Un ``pandas.DataFrame`` prêt à exporter dans ``results/tables/``.
    """
    import pandas as pd

    colonnes = {
        "cout": ("cout_reference", "cout_optimise"),
        "violation": ("violation_reference", "violation_optimise"),
        "satisfaction_moyenne": (
            "satisfaction_moyenne_reference",
            "satisfaction_moyenne_optimise",
        ),
        "ecart_type_satisfaction": (
            "ecart_type_reference",
            "ecart_type_optimise",
        ),
        "minimum_satisfaction": (
            "minimum_satisfaction_reference",
            "minimum_satisfaction_optimise",
        ),
    }
    lignes = []
    for nom, (reference, optimise) in colonnes.items():
        moyenne_reference = float(comparaison[reference].mean())
        moyenne_optimise = float(comparaison[optimise].mean())
        ecart_relatif = (
            (moyenne_optimise - moyenne_reference) / moyenne_reference
            if moyenne_reference != 0
            else np.nan
        )
        lignes.append({
            "metrique": nom,
            "reference_moyenne": moyenne_reference,
            "reference_ecart_type": float(comparaison[reference].std(ddof=1)),
            "optimise_moyenne": moyenne_optimise,
            "optimise_ecart_type": float(comparaison[optimise].std(ddof=1)),
            "ecart_relatif": ecart_relatif,
        })
    return pd.DataFrame(lignes)


def test_significativite(couts_reference: np.ndarray, couts_optimise: np.ndarray) -> dict:
    """Teste si l'écart de coût entre les deux stratégies est statistiquement réel.

    Sans ce test, la comparaison reste descriptive : « q* coûte moins cher sur
    nos tirages » ne dit pas si l'écart survit à l'incertitude de simulation.

    Choix à justifier dans le rapport : les deux stratégies sont évaluées **sur
    les mêmes scénarios**, donc les échantillons sont appariés. Un test apparié
    est plus puissant qu'un test à deux échantillons indépendants, et appliquer
    ce dernier ici serait une erreur de méthode, pas seulement un choix
    sous-optimal.

    Returns:
        Statistique de test, p-valeur, et taille d'effet.
    """
    from scipy import stats

    reference = np.asarray(couts_reference, dtype=float)
    optimise = np.asarray(couts_optimise, dtype=float)
    if reference.shape != optimise.shape or reference.ndim != 1:
        raise ValueError("Les deux vecteurs de coûts doivent avoir la même forme 1D.")
    if reference.size < 2:
        raise ValueError("Le test apparié demande au moins deux scénarios.")

    differences = reference - optimise
    test = stats.ttest_rel(reference, optimise)
    ecart_type = float(np.std(differences, ddof=1))
    taille_effet = float(np.mean(differences) / ecart_type) if ecart_type > 0 else np.inf
    return {
        "statistique": float(test.statistic),
        "p_valeur": float(test.pvalue),
        "difference_moyenne": float(np.mean(differences)),
        "taille_effet_cohen_d": taille_effet,
        "n_scenarios": int(reference.size),
    }
