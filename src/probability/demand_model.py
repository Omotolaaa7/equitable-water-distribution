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


def parametres_demande(reseau: Union[dict, object]) -> tuple[np.ndarray, np.ndarray]:
    """Extrait les vecteurs (µ_i) et (σ_i) dans l'ordre des quartiers.

    Args:
        reseau: Dictionnaire de configuration (issu de network_config.json)
                ou objet réseau de Membre 1.

    Returns:
        Le couple (mu, sigma), chacun de longueur |quartiers|.
    """
    if isinstance(reseau, dict):
        if "districts" in reseau:
            mu = [float(d["mu"]) for d in reseau["districts"]]
            sigma = [float(d["sigma"]) for d in reseau["districts"]]
        elif "demands" in reseau:
            mu = [float(reseau["demands"][q]["mu"]) for q in reseau["demands"]]
            sigma = [float(reseau["demands"][q]["sigma"]) for q in reseau["demands"]]
        else:
            mu = [25.0, 40.0, 35.0, 45.0, 40.0, 50.0, 30.0, 35.0]
            sigma = [5.0, 7.0, 6.0, 8.0, 7.0, 9.0, 5.0, 6.0]
    elif hasattr(reseau, "quartiers"):
        mu = [float(getattr(q, "mu", 35.0)) for q in reseau.quartiers]
        sigma = [float(getattr(q, "sigma", 6.0)) for q in reseau.quartiers]
    else:
        mu = [25.0, 40.0, 35.0, 45.0, 40.0, 50.0, 30.0, 35.0]
        sigma = [5.0, 7.0, 6.0, 8.0, 7.0, 9.0, 5.0, 6.0]

    return np.array(mu, dtype=np.float64), np.array(sigma, dtype=np.float64)


def matrice_covariance(reseau: Union[dict, object]) -> np.ndarray:
    """Construit la matrice de covariance Σ des demandes des quartiers.

    Construction : Σ_ij = ρ_ij · σ_i · σ_j, avec ρ_ii = 1.
    Contrôle de définie-positivité inclus (valeurs propres strictement > 0).

    Returns:
        Σ, de forme (|quartiers|, |quartiers|).
    """
    mu, sigma = parametres_demande(reseau)
    n = len(mu)

    # 1. Extraction ou construction de la matrice de corrélation R
    if isinstance(reseau, dict) and "correlation_matrix" in reseau:
        R = np.array(reseau["correlation_matrix"], dtype=np.float64)
    elif isinstance(reseau, dict) and "correlations" in reseau:
        R = np.eye(n, dtype=np.float64)
        quartiers_ids = [d.get("id", f"Q{i+1}") for i, d in enumerate(reseau.get("districts", []))]
        for item in reseau["correlations"]:
            u = item.get("u") or item.get("district_1") or item.get("pair", [None, None])[0]
            v = item.get("v") or item.get("district_2") or item.get("pair", [None, None])[1]
            rho = float(item.get("rho") or item.get("correlation", 0.30))
            if u in quartiers_ids and v in quartiers_ids:
                i, j = quartiers_ids.index(u), quartiers_ids.index(v)
                R[i, j] = R[j, i] = rho
    else:
        # Modèle spatial par défaut (voisins directs = 0.40, 2 sauts = 0.15)
        R = np.eye(n, dtype=np.float64)
        adj_pairs = [(2,3), (3,4), (2,4), (4,5), (3,6), (5,6), (6,7), (7,8), (6,8)]
        for u, v in adj_pairs:
            if u <= n and v <= n:
                R[u-1, v-1] = R[v-1, u-1] = 0.40
        two_hop = [(2,5), (2,6), (3,5), (4,6), (5,7), (5,8)]
        for u, v in two_hop:
            if u <= n and v <= n:
                R[u-1, v-1] = R[v-1, u-1] = 0.15

    # 2. Covariance Sigma = D_sigma * R * D_sigma
    D_sigma = np.diag(sigma)
    Sigma = D_sigma @ R @ D_sigma

    # 3. Contrôle des valeurs propres
    valeurs_propres = np.linalg.eigvalsh(Sigma)
    if np.any(valeurs_propres <= 0):
        min_vp = np.min(valeurs_propres)
        raise ValueError(
            f"La matrice de covariance Σ n'est pas définie positive ! Valeur propre minimale : {min_vp:.4e}"
        )

    return Sigma


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
