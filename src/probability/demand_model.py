"""Modèle de demande D_i ~ N(µ_i, σ_i²), estimateurs et intervalles de confiance.

Responsable : M3, en collaboration avec M6.
Dépend de : la topologie de M1 (nombre de quartiers, ordres de grandeur).
Alimente : M5 (paramètres nécessaires au Monte-Carlo).
Étape 4 du pipeline.

Le sujet impose la loi gaussienne, mais l'imposer n'est pas la justifier. La
section 1.7 du plan est explicite : contrairement au Thème 1, le sujet ne
réclame pas de démonstration par le théorème central limite, mais une
justification reste attendue, et la négliger est listée en section 14 parmi les
erreurs à éviter.

Argument à développer dans le rapport : la demande d'un quartier est la somme
d'un grand nombre de consommations individuelles à peu près indépendantes et de
faible amplitude devant le total, ce qui place le TCL en position d'argument
recevable. Argument à ne pas taire non plus : une gaussienne autorise des
demandes négatives. Avec σ_i entre 12 % et 28 % de µ_i, P(D_i < 0) reste
négligeable, mais le rapport doit le chiffrer plutôt que l'affirmer, et dire ce
que le code fait des tirages négatifs s'il en survient.
"""

from __future__ import annotations

import numpy as np


def parametres_demande(reseau) -> tuple[np.ndarray, np.ndarray]:
    """Extrait les vecteurs (µ_i) et (σ_i) dans l'ordre des quartiers.

    Returns:
        Le couple (mu, sigma), chacun de longueur |quartiers|.
    """
    raise NotImplementedError("M3, Étape 4.")


def matrice_covariance(reseau) -> np.ndarray:
    """Construit la matrice de covariance Σ des demandes des quartiers.

    Les quartiers voisins ne sont pas indépendants : une chaleur inhabituelle
    ou une coupure chez le voisin fait bouger plusieurs demandes ensemble. Le
    fichier de configuration déclare des groupes corrélés avec leur ρ.

    Construction : Σ_ij = ρ_ij · σ_i · σ_j, avec ρ_ii = 1.

    Piège à vérifier, pas à supposer : une matrice de corrélation assemblée par
    blocs à la main n'est pas automatiquement semi-définie positive. Si elle ne
    l'est pas, elle ne correspond à aucune loi gaussienne réelle et la
    factorisation de Cholesky de ``echantillonner`` échouera. Contrôler le signe
    des valeurs propres ici, et le signaler franchement plutôt que de corriger
    en silence.

    Returns:
        Σ, de forme (|quartiers|, |quartiers|).
    """
    raise NotImplementedError("M3, Étape 4.")


def echantillonner(
    mu: np.ndarray,
    covariance: np.ndarray,
    n_tirages: int,
    generateur: np.random.Generator,
) -> np.ndarray:
    """Tire n scénarios de demande selon la loi gaussienne multivariée.

    Passer un ``numpy.random.Generator`` explicite plutôt que d'appeler
    ``numpy.random`` directement : sans graine maîtrisée, aucun résultat du
    rapport n'est reproductible, et un correcteur qui relance le code n'obtient
    pas les chiffres cités.

    Args:
        mu: vecteur des demandes moyennes.
        covariance: matrice Σ.
        n_tirages: nombre N de scénarios.
        generateur: générateur aléatoire à graine fixée.

    Returns:
        Un tableau (n_tirages, |quartiers|).
    """
    raise NotImplementedError("M3 avec M5, Étape 4.")


def estimateur_moyenne(echantillon: np.ndarray) -> np.ndarray:
    """Moyenne empirique de chaque quartier.

    À écrire dans le rapport avant de la coder :

        µ̂_i = (1/n) Σ_k D_i^(k)

    estimateur sans biais de µ_i.
    """
    raise NotImplementedError("M3, Étape 4.")


def estimateur_variance(echantillon: np.ndarray) -> np.ndarray:
    """Variance empirique corrigée de chaque quartier.

        σ̂_i² = (1/(n−1)) Σ_k (D_i^(k) − µ̂_i)²

    Le diviseur n−1 et non n : c'est la correction de Bessel, et c'est ce qui
    rend l'estimateur sans biais. Numpy utilise n par défaut : il faut donc
    passer ``ddof=1`` explicitement. C'est une erreur silencieuse classique, et
    elle se propage jusque dans les intervalles de confiance.
    """
    raise NotImplementedError("M3, Étape 4.")


def intervalle_confiance_moyenne(
    echantillon: np.ndarray, niveau: float = 0.95
) -> tuple[np.ndarray, np.ndarray]:
    """Intervalle de confiance bilatéral sur µ_i.

    σ étant estimé et non connu, la statistique suit une loi de Student à n−1
    degrés de liberté, pas une loi normale :

        IC = [ µ̂_i ± t_{n−1, 1−α/2} · σ̂_i / √n ]

    Sur les grands échantillons Monte-Carlo la différence avec le quantile
    gaussien devient négligeable, mais c'est la justification du choix qui est
    notée, pas l'écart numérique.

    Args:
        echantillon: tableau (n, |quartiers|).
        niveau: niveau de confiance, 0.95 par défaut.

    Returns:
        Le couple (bornes_inf, bornes_sup).
    """
    raise NotImplementedError("M3, Étape 4. Livrable : tableau des estimateurs et IC.")


def correlations_empiriques(echantillon: np.ndarray) -> np.ndarray:
    """Matrice de corrélation empirique entre quartiers.

    Sert de contrôle de cohérence : les corrélations retrouvées sur les tirages
    doivent redonner celles déclarées dans la configuration. Un écart important
    signale une erreur dans ``matrice_covariance`` ou dans l'échantillonnage,
    et vaut mieux d'être détecté ici que six expériences plus loin.
    """
    raise NotImplementedError("M3, Étape 4.")


def quartiers_atypiques(
    historique: np.ndarray, mu_prevu: np.ndarray, niveau: float = 0.95
) -> dict[str, float]:
    """Identifie les quartiers dont la demande s'écarte régulièrement des prévisions.

    Support de l'Expérience 6. Pour chaque quartier, on mesure la fréquence à
    laquelle la demande observée sort de l'intervalle de confiance construit sur
    la demande prévue. Un quartier bien modélisé sort de son IC à 95 % dans
    environ 5 % des cas : c'est le repère par rapport auquel « atypique » se
    définit, et sans lui le chiffre brut ne veut rien dire.

    Returns:
        Fréquence de dépassement par quartier.
    """
    raise NotImplementedError("M3, Expérience 6.")
