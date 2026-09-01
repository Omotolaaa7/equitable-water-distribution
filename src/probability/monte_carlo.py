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

from .demand_model import (
    correlations_empiriques,
    echantillonner,
    estimateur_moyenne,
    estimateur_variance,
    matrice_covariance,
    parametres_demande,
)

# Graine par defaut. Fixee ici plutot qu'a chaque appel, pour qu'un oubli
# donne un resultat reproductible au lieu d'un resultat different a chaque
# execution.
GRAINE_PAR_DEFAUT = 42


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
    mu, _ = parametres_demande(reseau)
    covariance = matrice_covariance(reseau)
    generateur = np.random.default_rng(
        GRAINE_PAR_DEFAUT if graine is None else graine
    )
    return echantillonner(mu, covariance, n_tirages, generateur)


def agreger(valeurs: np.ndarray, quantiles=(0.05, 0.25, 0.5, 0.75, 0.95)) -> StatistiquesMonteCarlo:
    """Calcule moyenne, variance, erreur standard et quantiles d'une population.

    L'erreur standard vaut σ̂/√N. C'est la forme concrète du résultat théorique
    à établir à l'Étape 5 : l'erreur d'estimation Monte-Carlo décroît en 1/√N.
    Conséquence à énoncer explicitement dans le rapport, parce qu'elle est
    contre-intuitive et qu'elle justifie le dimensionnement retenu : diviser
    l'erreur par deux coûte *quatre* fois plus de tirages.
    """
    valeurs = np.asarray(valeurs, dtype=float).ravel()
    n = valeurs.size
    if n < 2:
        raise ValueError(
            f'Agrégation impossible sur {n} valeur(s) : la variance corrigée demande au moins 2 tirages.'
        )

    ecart_type = float(np.std(valeurs, ddof=1))
    return StatistiquesMonteCarlo(
        moyenne=float(np.mean(valeurs)),
        variance=float(np.var(valeurs, ddof=1)),
        erreur_standard=erreur_estimation(ecart_type, n),
        quantiles={float(niveau): float(np.quantile(valeurs, niveau))
                   for niveau in quantiles},
        n_tirages=n,
    )


def erreur_estimation(ecart_type: float, n_tirages: int) -> float:
    """Erreur standard d'estimation Monte-Carlo, σ̂/√N.

    Fonction volontairement triviale et isolée : c'est la formule que
    l'Expérience 2 confronte à la décroissance mesurée quand N augmente. La
    séparer permet de la tester seule.
    """
    if n_tirages < 1:
        raise ValueError(f'n_tirages doit valoir au moins 1, reçu {n_tirages}.')
    return float(ecart_type) / np.sqrt(float(n_tirages))


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
    valeurs = np.asarray(valeurs, dtype=float).ravel()
    resultats = {}

    for taille in tailles:
        if taille > valeurs.size:
            raise ValueError(
                f'Taille {taille} demandée alors que la population n\'en compte que {valeurs.size}. '
                'Générer davantage de tirages plutôt que de réduire la taille en silence.'
            )
        # Prefixe de la population, et non un tirage a part : on veut voir la
        # meme experience s'affiner, pas comparer trois experiences differentes.
        resultats[int(taille)] = agreger(valeurs[:taille])

    return resultats
