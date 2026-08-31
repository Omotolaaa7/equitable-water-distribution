"""
Modèle de demande D_i ~ N(µ_i, σ_i²), estimateurs et intervalles de confiance.

Responsable : M3, en collaboration avec M6.
Dépend de : la topologie de M1 (nombre de quartiers, ordres de grandeur).
Alimente : M5 (paramètres nécessaires au Monte-Carlo).
Étape 4 du pipeline.
"""

from __future__ import annotations
import json
import os
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Lecture du réseau : une seule source de vérité
# ---------------------------------------------------------------------------
#
# Le fichier ``data/network_config.json``, tenu par le Membre 1, nomme ses cases
# en français : ``noeuds`` contenant ``quartiers``, et ``correlations_voisinage``.
# Les fonctions ci-dessous lisent ces noms.
#
# Il n'y a volontairement plus aucune valeur de repli codée en dur. Un repli
# silencieux faisait travailler tout le projet sur des chiffres absents du
# rapport, sans qu'aucune erreur ne se déclenche. Une structure non reconnue
# lève désormais une exception qui dit ce qu'elle a trouvé.


def _quartiers_depuis(reseau) -> tuple[list, np.ndarray, np.ndarray]:
    """Retourne (identifiants, mu, sigma) des quartiers, dans l'ordre du réseau.

    Accepte l'objet ``Reseau`` de ``data/generate_network.py``, le dictionnaire
    issu directement de ``network_config.json``, ou les variantes anglaises
    ``districts`` et ``demands`` conservées par compatibilité.

    Raises:
        ValueError: si la structure ne contient aucun quartier lisible.
        TypeError: si l'objet reçu n'est ni un réseau ni un dictionnaire.
    """
    if hasattr(reseau, "quartiers"):
        quartiers = list(reseau.quartiers)
        identifiants = [
            getattr(q, "identifiant", getattr(q, "id", f"Q{i + 1}"))
            for i, q in enumerate(quartiers)
        ]
        mu = [float(q.mu) for q in quartiers]
        sigma = [float(q.sigma) for q in quartiers]
        return identifiants, np.array(mu, dtype=np.float64), np.array(sigma, dtype=np.float64)

    if isinstance(reseau, dict):
        quartiers = reseau.get("noeuds", {}).get("quartiers")
        if quartiers is None:
            quartiers = reseau.get("districts")
        if quartiers is not None:
            identifiants = [str(q.get("id", f"Q{i + 1}")) for i, q in enumerate(quartiers)]
            mu = [float(q["mu"]) for q in quartiers]
            sigma = [float(q["sigma"]) for q in quartiers]
            return identifiants, np.array(mu, dtype=np.float64), np.array(sigma, dtype=np.float64)
        if "demands" in reseau:
            identifiants = list(reseau["demands"])
            mu = [float(reseau["demands"][q]["mu"]) for q in identifiants]
            sigma = [float(reseau["demands"][q]["sigma"]) for q in identifiants]
            return identifiants, np.array(mu, dtype=np.float64), np.array(sigma, dtype=np.float64)
        raise ValueError(
            "Aucun quartier lisible dans la configuration. Clés trouvées à la racine : "
            f"{sorted(reseau)}. Attendu la clé 'noeuds' contenant 'quartiers'."
        )

    raise TypeError(
        f"Type de réseau non reconnu : {type(reseau).__name__}. Passer l'objet Reseau "
        "de data/generate_network.py, ou le dictionnaire de network_config.json."
    )


def _paires_correlees_depuis(reseau, identifiants: list) -> list:
    """Retourne les paires corrélées déclarées, sous forme (i, j, rho).

    Lit ``correlations_voisinage``, dont chaque entrée a la forme
    ``{"quartiers": ["Q2", "Q3"], "rho": 0.3}``. Une entrée citant plus de deux
    quartiers est traitée comme un groupe : toutes ses paires internes reçoivent
    le même rho.

    Une configuration sans déclaration de corrélation décrit des quartiers
    indépendants, et retourne une liste vide.
    """
    position = {identifiant: i for i, identifiant in enumerate(identifiants)}

    if isinstance(reseau, dict):
        declarations = reseau.get("correlations_voisinage") or reseau.get("correlations") or []
    else:
        declarations = list(getattr(reseau, "correlations_voisinage", []) or [])

    paires = []
    for item in declarations:
        rho = float(item.get("rho", item.get("correlation", 0.0)))
        groupe = item.get("quartiers") or item.get("pair") or [
            item.get("u") or item.get("district_1"),
            item.get("v") or item.get("district_2"),
        ]
        groupe = [g for g in groupe if g in position]
        for a in range(len(groupe)):
            for b in range(a + 1, len(groupe)):
                paires.append((position[groupe[a]], position[groupe[b]], rho))
    return paires


def parametres_demande(reseau) -> tuple[np.ndarray, np.ndarray]:
    """Extrait les vecteurs (µ_i) et (σ_i) dans l'ordre des quartiers.

    Args:
        reseau: l'objet ``Reseau`` du Membre 1, ou le dictionnaire de
            ``network_config.json``.

    Returns:
        Le couple (mu, sigma), chacun de longueur |quartiers|.
    """
    _, mu, sigma = _quartiers_depuis(reseau)
    return mu, sigma


def matrice_covariance(reseau) -> np.ndarray:
    """Construit la matrice de covariance Σ des demandes des quartiers.

    Construction : Σ_ij = ρ_ij · σ_i · σ_j, avec ρ_ii = 1. Les ρ_ij viennent
    exclusivement de ce que le Membre 1 déclare dans ``correlations_voisinage``.
    Toute paire non déclarée est supposée indépendante.

    Piège à vérifier plutôt qu'à supposer : une matrice de corrélation assemblée
    paire par paire n'est pas automatiquement définie positive. Si elle ne l'est
    pas, elle ne correspond à aucune loi gaussienne réelle et l'échantillonnage
    échouera. Le contrôle est fait ici, et il lève plutôt que de corriger en
    silence.

    Returns:
        Σ, de forme (|quartiers|, |quartiers|).
    """
    identifiants, _, sigma = _quartiers_depuis(reseau)
    n = len(identifiants)

    R = np.eye(n, dtype=np.float64)
    for i, j, rho in _paires_correlees_depuis(reseau, identifiants):
        R[i, j] = R[j, i] = rho

    D_sigma = np.diag(sigma)
    Sigma = D_sigma @ R @ D_sigma

    valeurs_propres = np.linalg.eigvalsh(Sigma)
    if np.any(valeurs_propres <= 0):
        raise ValueError(
            "La matrice de covariance Σ n'est pas définie positive. Valeur propre "
            f"minimale : {np.min(valeurs_propres):.4e}. Les corrélations déclarées "
            "dans network_config.json ne décrivent aucune loi gaussienne réelle."
        )

    return Sigma


def paires_voisinage_depuis_topologie(
    reseau, rho_voisin: float = 0.40, rho_deux_sauts: float = 0.15
) -> list:
    """Propose des corrélations déduites de la topologie réelle du réseau.

    Deux quartiers reliés par une conduite reçoivent ``rho_voisin``, deux
    quartiers séparés par exactement deux conduites reçoivent ``rho_deux_sauts``.

    Cette règle est celle proposée par le Membre 3. Elle ne s'applique pas toute
    seule : la fonction retourne des entrées prêtes à coller dans
    ``correlations_voisinage`` de ``network_config.json``, pour que le fichier
    du Membre 1 reste la seule source de vérité.

    Contrairement à une liste de paires écrite à la main, celle-ci se recalcule
    si le Membre 1 modifie la topologie.

    Returns:
        Une liste d'entrées ``{"quartiers": [a, b], "rho": ρ}``.
    """
    identifiants, _, _ = _quartiers_depuis(reseau)
    ensemble = set(identifiants)

    voisins = {identifiant: set() for identifiant in identifiants}
    conduites = reseau["conduites"] if isinstance(reseau, dict) else reseau.conduites
    for c in conduites:
        depart = c["de"] if isinstance(c, dict) else c.source
        arrivee = c["vers"] if isinstance(c, dict) else c.cible
        if depart in ensemble and arrivee in ensemble:
            voisins[depart].add(arrivee)
            voisins[arrivee].add(depart)

    entrees = []
    for a_index, a in enumerate(identifiants):
        for b in identifiants[a_index + 1:]:
            if b in voisins[a]:
                entrees.append({"quartiers": [a, b], "rho": rho_voisin})
            elif voisins[a] & voisins[b]:
                entrees.append({"quartiers": [a, b], "rho": rho_deux_sauts})
    return entrees


def echantillonner(
    mu: np.ndarray,
    covariance: np.ndarray,
    n_tirages: int,
    generateur: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Tire n scénarios de demande selon la loi gaussienne multivariée D ~ N(mu, Sigma).

    Args:
        mu: vecteur des demandes moyennes (longueur p).
        covariance: matrice Σ (p x p).
        n_tirages: nombre N de scénarios.
        generateur: générateur aléatoire à graine fixée pour reproductibilité.

    Returns:
        Un tableau numpy de forme (n_tirages, p) avec non-négativité physique.
    """
    if generateur is None:
        generateur = np.random.default_rng(42)

    # Tirage multivarié gaussien reproductible
    tirages = generateur.multivariate_normal(mean=mu, cov=covariance, size=n_tirages)
    
    # Préservation de la positivité physique
    return np.clip(tirages, a_min=0.0, a_max=None)


def estimateur_moyenne(echantillon: np.ndarray) -> np.ndarray:
    """Moyenne empirique sans biais de chaque quartier :
    
        µ̂_i = (1/n) Σ_k D_i^(k)
    """
    return np.mean(echantillon, axis=0)


def estimateur_variance(echantillon: np.ndarray) -> np.ndarray:
    """Variance empirique corrigée sans biais de chaque quartier (correction de Bessel ddof=1) :
    
        σ̂_i² = (1/(n−1)) Σ_k (D_i^(k) − µ̂_i)²
    """
    return np.var(echantillon, axis=0, ddof=1)


def intervalle_confiance_moyenne(
    echantillon: np.ndarray, niveau: float = 0.95
) -> tuple[np.ndarray, np.ndarray]:
    """Intervalle de confiance bilatéral de Student à (n - 1) degrés de liberté sur µ_i :

        IC = [ µ̂_i ± t_{n−1, 1−α/2} · S_i / √n ]

    Returns:
        Le couple (bornes_inf, bornes_sup).
    """
    n = echantillon.shape[0]
    mu_hat = estimateur_moyenne(echantillon)
    s_hat = np.sqrt(estimateur_variance(echantillon))

    # Quantile Student t(n-1)
    t_crit = stats.t.ppf((1.0 + niveau) / 2.0, df=n - 1)
    marge = t_crit * (s_hat / np.sqrt(n))

    return mu_hat - marge, mu_hat + marge


def correlations_empiriques(echantillon: np.ndarray) -> np.ndarray:
    """Matrice de corrélation empirique de Pearson entre quartiers."""
    return np.corrcoef(echantillon, rowvar=False)


def quartiers_atypiques(
    historique: np.ndarray, mu_prevu: np.ndarray, niveau: float = 0.95
) -> dict[str, float]:
    """Identifie les quartiers dont la demande s'écarte régulièrement des prévisions.
    
    Support de l'Expérience 6. Calcule pour chaque quartier la fréquence
    de dépassement de son intervalle prévisionnel bilatéral.

    Returns:
        Dictionnaire { 'Q_i': frequence_depassement }.
    """
    n_jours, n_quartiers = historique.shape
    std_estime = np.sqrt(estimateur_variance(historique))
    
    # Bornes théoriques à (1 - alpha)
    z_crit = stats.norm.ppf((1.0 + niveau) / 2.0)
    borne_inf = mu_prevu - z_crit * std_estime
    borne_sup = mu_prevu + z_crit * std_estime

    frequences = {}
    for i in range(n_quartiers):
        depassements = (historique[:, i] < borne_inf[i]) | (historique[:, i] > borne_sup[i])
        freq = float(np.mean(depassements))
        frequences[f"Q{i+1}"] = freq

    return frequences


# =============================================================================
# CLASSE WRAPPER POUR FACILITER L'UTILISATION GLOBALE (DEMANDMODEL)
# =============================================================================

class DemandModel:
    """Modèle probabiliste orienté-objet basé sur network_config.json."""

    def __init__(self, config_path: str = "data/network_config.json"):
        self.config_path = config_path
        self.config = self._load_json(config_path)

        self.mu, self.sigma = parametres_demande(self.config)
        self.Sigma = matrice_covariance(self.config)
        self.n_districts = len(self.mu)
        self.quartiers = [f"Q{i+1}" for i in range(self.n_districts)]
        self.reservoirs = ["R1", "R2"]
        self.n_nodes = len(self.reservoirs) + self.n_districts

        # Matrice R
        D_inv = np.diag(1.0 / self.sigma)
        self.R = D_inv @ self.Sigma @ D_inv

    def _load_json(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        alt = os.path.join("..", "..", path)
        if os.path.exists(alt):
            with open(alt, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def sample_demands(self, n_samples: int = 1000, seed: Optional[int] = 42) -> np.ndarray:
        gen = np.random.default_rng(seed)
        return echantillonner(self.mu, self.Sigma, n_samples, gen)

    def generate_full_rhs(
        self,
        demand_vector: np.ndarray,
        split_ratio: Tuple[float, float] = (0.5, 0.5)
    ) -> np.ndarray:
        D_total = np.sum(demand_vector)
        b = np.zeros(self.n_nodes, dtype=np.float64)
        b[0] = -split_ratio[0] * D_total
        b[1] = -split_ratio[1] * D_total
        b[2:] = demand_vector
        return b

    def compute_statistics(self, samples: np.ndarray, confidence_level: float = 0.95) -> Dict:
        mean_emp = estimateur_moyenne(samples)
        var_emp = estimateur_variance(samples)
        std_emp = np.sqrt(var_emp)
        ic_inf, ic_sup = intervalle_confiance_moyenne(samples, niveau=confidence_level)
        return {
            "mean_emp": mean_emp,
            "std_emp": std_emp,
            "ic_lower": ic_inf,
            "ic_upper": ic_sup,
            "corr_emp": correlations_empiriques(samples)
        }
