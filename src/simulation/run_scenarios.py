"""Résolution du problème d'optimisation sur un ensemble de scénarios.

Responsable : M5.
Dépend de : Étape 5 (scénarios de M3/M5) et Étape 9 (solveur validé).
Alimente : M6 pour la comparaison à la stratégie de référence.
Étape 10 du pipeline.

Le sujet demande de tester q* sur des situations variées, pas seulement sur la
demande moyenne. C'est ce que ce module industrialise.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ResultatScenario:
    """Ce qu'on retient d'un scénario résolu.

    On conserve à la fois ``cout_technique`` et ``violation`` : une solution
    peut sembler très bon marché simplement parce qu'elle ne respecte pas la
    conservation des flux. Présenter le coût sans la violation associée
    donnerait une comparaison trompeuse.
    """

    indice: int
    demandes: np.ndarray
    q_optimal: np.ndarray
    cout_technique: float
    violation: float
    n_iterations: int
    a_converge: bool


def resoudre_scenario(reseau, A: np.ndarray, demandes: np.ndarray, mu: float, **options) -> ResultatScenario:
    """Résout le problème pénalisé pour un scénario de demande donné.

    Enchaînement : ``construire_second_membre`` pour obtenir b, puis
    ``descente_projetee``, puis calcul des métriques.
    """
    raise NotImplementedError("M5, Étape 10, dépend d'un solveur fonctionnel.")


def resoudre_tous(
    reseau, A: np.ndarray, scenarios: np.ndarray, mu: float, **options
) -> list[ResultatScenario]:
    """Résout le problème sur chaque scénario d'un jeu Monte-Carlo.

    Args:
        scenarios: tableau (N, |quartiers|) issu de ``generer_scenarios``.

    Returns:
        Un résultat par scénario, dans l'ordre.

    Attention au coût de calcul : N scénarios × k itérations de descente. Sur
    N = 10 000, une descente lente devient une expérience qui ne tourne plus.
    Si le temps devient un obstacle, le réduire en resserrant la tolérance ou
    en partant d'un q_initial pertinent, mais jamais en baissant N en silence, ce
    qui dégraderait la fiabilité statistique sans que le rapport le signale
    (erreur listée en section 14 du plan).
    """
    raise NotImplementedError("M5, Étape 10.")


def scenarios_de_stress(reseau, quantile: float = 0.95) -> np.ndarray:
    """Construit des scénarios extrêmes plutôt que typiques.

    La section 10 du plan demande des scénarios moyen, favorable et
    défavorable. Un plan de distribution qui ne tient que sur la demande
    moyenne n'a aucun intérêt opérationnel : c'est sur les pointes que le
    réseau casse.

    Args:
        quantile: niveau de sévérité, 0.95 pour une demande haute.
    """
    raise NotImplementedError("M5, Étape 10.")
