"""Simulation Monte-Carlo : scénarios de demande et statistiques agrégées.

Responsable : M5, en collaboration avec M3.
Dépend de : le modèle de demande figé par M3 (Étape 4).
Alimente : ``src.simulation.run_scenarios`` et les Expériences 2 et 6.
Étape 5 du pipeline.

Le rôle de ce module est de transformer un modèle probabiliste en scénarios
exploitables. Ce qui est noté, ce n'est pas de savoir tirer des nombres au
hasard, c'est de savoir *avec quelle précision* on connaît les statistiques
qu'on en déduit.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StatistiquesMonteCarlo:
    """Résumé d'une population de tirages.

    ``erreur_standard`` n'est pas décoratif : c'est lui qui permet de dire si
    l'écart mesuré entre deux stratégies est réel ou dans le bruit de la
    simulation. Une comparaison sans barre d'erreur n'est pas une comparaison.
    """

    moyenne: float
    variance: float
    erreur_standard: float
    quantiles: dict[float, float]
    n_tirages: int


def generer_scenarios(
    reseau, n_tirages: int, graine: int | None = None
) -> np.ndarray:
    """Génère N scénarios de demande à partir du modèle de M3.

    Args:
        reseau: le ``Reseau``.
        n_tirages: nombre de scénarios.
        graine: graine du générateur. Fixée par défaut dans la configuration,
            car un résultat non reproductible n'est pas un résultat.

    Returns:
        Un tableau (n_tirages, |quartiers|).
    """
    raise NotImplementedError("M5 avec M3, Étape 5.")


def agreger(valeurs: np.ndarray, quantiles=(0.05, 0.25, 0.5, 0.75, 0.95)) -> StatistiquesMonteCarlo:
    """Calcule moyenne, variance, erreur standard et quantiles d'une population.

    L'erreur standard vaut σ̂/√N. C'est la forme concrète du résultat théorique
    à établir à l'Étape 5 : l'erreur d'estimation Monte-Carlo décroît en 1/√N.
    Conséquence à énoncer explicitement dans le rapport, parce qu'elle est
    contre-intuitive et qu'elle justifie le dimensionnement retenu : diviser
    l'erreur par deux coûte *quatre* fois plus de tirages.
    """
    raise NotImplementedError("M5, Étape 5.")


def erreur_estimation(ecart_type: float, n_tirages: int) -> float:
    """Erreur standard d'estimation Monte-Carlo, σ̂/√N.

    Fonction volontairement triviale et isolée : c'est la formule que
    l'Expérience 2 confronte à la décroissance mesurée quand N augmente. La
    séparer permet de la tester seule.
    """
    raise NotImplementedError("M5, Étape 5.")


def convergence_par_taille(
    valeurs: np.ndarray, tailles: tuple[int, ...] = (100, 1_000, 10_000)
) -> dict[int, StatistiquesMonteCarlo]:
    """Recalcule les statistiques à plusieurs tailles d'échantillon croissantes.

    Support de la vérification empirique de la loi des grands nombres : la
    moyenne empirique doit se stabiliser et l'erreur standard décroître en
    1/√N. C'est une des confrontations théorie/expérience exigées par le sujet.

    Args:
        valeurs: population complète de tirages.
        tailles: sous-tailles à évaluer, croissantes.

    Returns:
        Les statistiques par taille d'échantillon.
    """
    raise NotImplementedError("M5, Étape 5, support de l'Expérience 2.")
