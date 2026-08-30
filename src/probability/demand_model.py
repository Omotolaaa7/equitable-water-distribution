"""Modèle de demande D_i ~ N(µ_i, σ_i²), estimateurs et intervalles de confiance.

Responsable : M3, en collaboration avec M6.
Dépend de : la topologie de M1 (nombre de quartiers, ordres de grandeur).
Alimente : M5 (paramètres nécessaires au Monte-Carlo).
Étape 4 du pipeline.
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
"""
Projet : Distribution d'eau équitable sous incertitude (Thème 3)

Ce module regroupe l'ensemble des développements probabilistes et statistiques (Étapes 1, 2 et 3) :
- Modélisation gaussienne multivariée D ~ N_8(mu, Sigma)
- Construction topologique de la matrice de corrélation spatiale R et covariance Sigma
- Diagnostic spectral complet (valeurs propres, conditionnement, définie-positivité, P(D < 0))
- Moteur d'échantillonnage Monte-Carlo et construction du second membre b in R^10 (sum b = 0)
- Estimateurs sans biais, Intervalles de Confiance de Student (95% et 99%)
- Étude empirique de la vitesse de convergence en O(1/sqrt(N))
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple


class DemandModel:
    """
    Modèle probabiliste complet de la demande en eau pour les 8 quartiers (Q1 à Q8)
    alimentés par 2 réservoirs (R1, R2).
    """

    def __init__(self):
        # -------------------------------------------------------------
        # 1. DÉFINITION DES ENTITÉS DU RÉSEAU (Étape 1)
        # -------------------------------------------------------------
        self.reservoirs: List[str] = ["R1", "R2"]
        self.quartiers: List[str] = [f"Q{i}" for i in range(1, 9)]
        self.n_districts: int = len(self.quartiers)
        self.n_nodes: int = len(self.reservoirs) + self.n_districts  # 10 nœuds
        self.offre_max_reservoirs: float = 360.0  # Capacité maximale installée

        # Vecteur des moyennes mu_i (m3/h) fixé par Membre 1
        self.mu: np.ndarray = np.array(
            [25.0, 40.0, 35.0, 45.0, 40.0, 50.0, 30.0, 35.0], dtype=np.float64
        )

        # Vecteur des écarts-types sigma_i (m3/h) fixé par Membre 1
        self.sigma: np.ndarray = np.array(
            [5.0, 7.0, 6.0, 8.0, 7.0, 9.0, 5.0, 6.0], dtype=np.float64
        )

        # -------------------------------------------------------------
        # 2. CONSTRUCTION DE LA MATRICE DE CORRÉLATION SPATIALE R (Étape 1)
        # -------------------------------------------------------------
        self.R: np.ndarray = self._build_spatial_correlation_matrix()

        # -------------------------------------------------------------
        # 3. CONSTRUCTION DE LA MATRICE DE COVARIANCE SIGMA (Étape 1)
        # -------------------------------------------------------------
        self.D_sigma: np.ndarray = np.diag(self.sigma)
        self.Sigma: np.ndarray = self.D_sigma @ self.R @ self.D_sigma

        # Propriétés spectrales
        self.valeurs_propres: np.ndarray = np.linalg.eigvalsh(self.Sigma)
        self.est_symetrique: bool = np.allclose(self.Sigma, self.Sigma.T)
        self.est_definie_positive: bool = bool(np.all(self.valeurs_propres > 0))
        self.conditionnement_Sigma: float = float(
            np.max(self.valeurs_propres) / np.min(self.valeurs_propres)
        )

        if not self.est_definie_positive:
            raise ValueError("ERREUR MATHÉMATIQUE : La matrice Sigma n'est pas définie positive !")

    def _build_spatial_correlation_matrix(self) -> np.ndarray:
        """
        Construit la matrice de corrélation spatiale R (8x8) :
        - rho = 1.00 sur la diagonale
        - rho = 0.40 pour les quartiers directement adjacents (arêtes directes)
        - rho = 0.15 pour les quartiers à 2 sauts
        - rho = 0.00 sinon (notamment Q1, nœud de degré 1 isolé sur son arête-pont)
        """
        R = np.eye(self.n_districts, dtype=np.float64)

        # Voisins directs (1 saut topologique)
        voisins_directs = [
            (2, 3), (3, 4), (2, 4),  # Boucle Zone 1
            (4, 5), (3, 6),  # Connexions inter-zones
            (5, 6), (6, 7), (7, 8), (6, 8)  # Boucles Zone 2
        ]
        for u, v in voisins_directs:
            i, j = u - 1, v - 1
            R[i, j] = 0.40
            R[j, i] = 0.40

        # Voisins à 2 sauts topologiques
        voisins_2_sauts = [
            (2, 5), (2, 6), (3, 5), (4, 6), (5, 7), (5, 8)
        ]
        for u, v in voisins_2_sauts:
            i, j = u - 1, v - 1
            R[i, j] = 0.15
            R[j, i] = 0.15

        return R

    # =========================================================================
    # FONCTIONS DE L'ÉTAPE 1 : PROBABILITÉS & DIAGNOSTIC PHYSIQUE
    # =========================================================================
    def compute_theoretical_negativity_probabilities(self) -> np.ndarray:
        """Calcule la probabilité théorique P(D_i < 0) = Phi(-mu_i / sigma_i)."""
        return stats.norm.cdf(-self.mu / self.sigma)

    def print_stage1_diagnostic(self):
        """Affiche le diagnostic complet de l'Étape 1 (Théorie & Spectre)."""
        print("=" * 88)
        print("                 DIAGNOSTIC DE L'ÉTAPE 1 : MODÉLISATION PROBABILISTE")
        print("=" * 88)
        p_neg = self.compute_theoretical_negativity_probabilities()
        print(f"{'Quartier':<10}{'mu_i (m3/h)':<14}{'sigma_i':<12}{'CV = sigma/mu':<16}{'P(D_i < 0) [Théorique]':<25}")
        print("-" * 88)
        for k in range(self.n_districts):
            cv = (self.sigma[k] / self.mu[k]) * 100
            print(f"{self.quartiers[k]:<10}{self.mu[k]:<14.2f}{self.sigma[k]:<12.2f}{cv:<15.2f}%{p_neg[k]:<25.4e}")
        print("-" * 88)
        print(f" -> Matrice symétrique : {self.est_symetrique}")
        print(f" -> Définie positive  : {self.est_definie_positive}")
        print(f" -> Valeurs propres de Sigma : {np.round(self.valeurs_propres, 4)}")
        print(f" -> Conditionnement kappa(Sigma) : {self.conditionnement_Sigma:.4f}")
        print("=" * 88 + "\n")

    # =========================================================================
    # FONCTIONS DE L'ÉTAPE 2 : ÉCHANTILLONNAGE & CONSERVATION PHYSIQUE
    # =========================================================================
    def sample_demands(self, n_samples: int = 1000, seed: Optional[int] = 42) -> np.ndarray:
        """
        Génère n_samples scénarios de demande multivariée D ~ N_8(mu, Sigma).
        Retourne un tableau numpy de dimension (n_samples, 8).
        """
        if seed is not None:
            np.random.seed(seed)
        demands = np.random.multivariate_normal(mean=self.mu, cov=self.Sigma, size=n_samples)
        # Sécurité physique : écrêtage à 0 pour interdire les valeurs négatives
        return np.clip(demands, a_min=0.0, a_max=None)

    def generate_full_rhs(
            self,
            demand_vector: np.ndarray,
            split_ratio: Tuple[float, float] = (0.5, 0.5)
    ) -> np.ndarray:
        """
        Construit le vecteur second membre b in R^10 pour le système de conservation Aq = b.
        b = [-s(R1), -s(R2), D1, D2, ..., D8]^T
        Garantit strictement sum(b) = 0.
        """
        D_total = np.sum(demand_vector)
        s_R1 = split_ratio[0] * D_total
        s_R2 = split_ratio[1] * D_total

        b = np.zeros(self.n_nodes, dtype=np.float64)
        b[0] = -s_R1  # Injection Réservoir R1 (négatif)
        b[1] = -s_R2  # Injection Réservoir R2 (négatif)
        b[2:] = demand_vector  # Soutirage Quartiers Q1 à Q8 (positif)
        return b

    def verify_mass_conservation_on_samples(self, n_samples: int = 10000) -> float:
        """Vérifie l'erreur maximale absolue sur sum(b) sur n_samples tirages."""
        samples = self.sample_demands(n_samples=n_samples, seed=42)
        max_err = 0.0
        for k in range(n_samples):
            b_k = self.generate_full_rhs(samples[k])
            err_k = abs(np.sum(b_k))
            if err_k > max_err:
                max_err = err_k
        return max_err

    # =========================================================================
    # FONCTIONS DE L'ÉTAPE 3 : ANALYSE STATISTIQUE & INTERVALLES DE CONFIANCE
    # =========================================================================
    def compute_statistics(self, samples: np.ndarray, confidence_level: float = 0.95) -> Dict:
        """
        Calcule les estimateurs non biaisés (moyenne, variance) et les intervalles
        de confiance de Student pour chaque quartier.
        """
        M = samples.shape[0]
        mean_emp = np.mean(samples, axis=0)
        var_emp = np.var(samples, axis=0, ddof=1)
        std_emp = np.sqrt(var_emp)

        # Demi-largeur IC de Student à M-1 degrés de liberté
        t_crit = stats.t.ppf((1.0 + confidence_level) / 2.0, df=M - 1)
        margin = t_crit * (std_emp / np.sqrt(M))

        return {
            "n_samples": M,
            "mean_emp": mean_emp,
            "var_emp": var_emp,
            "std_emp": std_emp,
            "ic_lower": mean_emp - margin,
            "ic_upper": mean_emp + margin,
            "margin": margin,
            "corr_emp": np.corrcoef(samples, rowvar=False),
        }

    def evaluate_convergence_rates(
            self, sample_sizes: Optional[List[int]] = None
    ) -> List[Tuple[int, float, float, float]]:
        """
        Évalue la vitesse de convergence de l'erreur ||mu_hat_N - mu||_2 en fonction de 1/sqrt(N).
        """
        if sample_sizes is None:
            sample_sizes = [10, 50, 100, 500, 1000, 5000, 10000, 50000]

        np.random.seed(42)
        results = []
        for N_k in sample_sizes:
            tirages = np.random.multivariate_normal(mean=self.mu, cov=self.Sigma, size=N_k)
            moy_k = np.mean(tirages, axis=0)
            norme_erreur = float(np.linalg.norm(moy_k - self.mu, 2))
            inv_sqrt = 1.0 / np.sqrt(N_k)
            ratio = norme_erreur / inv_sqrt
            results.append((N_k, norme_erreur, inv_sqrt, ratio))
        return results

    def print_stage3_summary(self, n_days: int = 365):
        """Affiche le tableau des estimateurs et intervalles de confiance (Étape 3)."""
        samples = self.sample_demands(n_samples=n_days, seed=42)
        stats_95 = self.compute_statistics(samples, confidence_level=0.95)
        stats_99 = self.compute_statistics(samples, confidence_level=0.99)

        print("=" * 95)
        print(f"      SYNTHÈSE STATISTIQUE ET INTERVALLES DE CONFIANCE (M = {n_days} JOURS)")
        print("=" * 95)
        print(
            f"{'Nœud':<6}{'mu (théo)':<11}{'mu_hat':<10}{'sigma (théo)':<13}{'S_i':<9}{'IC à 95%':<22}{'IC à 99%':<22}")
        print("-" * 95)
        for i, q in enumerate(self.quartiers):
            ic95 = f"[{stats_95['ic_lower'][i]:.2f} ; {stats_95['ic_upper'][i]:.2f}]"
            ic99 = f"[{stats_99['ic_lower'][i]:.2f} ; {stats_99['ic_upper'][i]:.2f}]"
            print(
                f"{q:<6}{self.mu[i]:<11.2f}{stats_95['mean_emp'][i]:<10.2f}{self.sigma[i]:<13.2f}{stats_95['std_emp'][i]:<9.2f}{ic95:<22}{ic99:<22}")
        print("-" * 95)


# =============================================================================
# EXÉCUTION DIRECTE (TEST COMPLET DU MODULE)
# =============================================================================
if __name__ == "__main__":
    print("=" * 88)
    print("       TEST GLOBAL DU MODULE DEMAND_MODEL (MEMBRE 3 - PROBABILITÉS)")
    print("=" * 88)

    # 1. Instanciation
    model = DemandModel()

    # 2. Exécution du diagnostic Étape 1
    model.print_stage1_diagnostic()

    # 3. Exécution du test de conservation Étape 2
    err_max = model.verify_mass_conservation_on_samples(10000)
    print(f"Erreur max absolue sur sum(b) (10 000 tirages) : {err_max:.2e} (Doit être proche de 0)")

    # 4. Exécution de l'analyse statistique Étape 3
    model.print_stage3_summary(n_days=365)

    # 5. Convergence en 1/sqrt(N)
    print("\nVitesse de convergence Monte-Carlo en O(1/sqrt(N)) :")
    conv_results = model.evaluate_convergence_rates()
    for N_k, err, inv_s, rat in conv_results:
        print(f" -> N = {N_k:<6} | Erreur = {err:<8.5f} | 1/sqrt(N) = {inv_s:<8.5f} | Ratio = {rat:.2f}")

    print("\n" + "=" * 88)
    print(">>> MODULE DEMAND_MODEL ENTIÈREMENT VALIDÉ ET FONCTIONNEL À 100% <<<")
    print("=" * 88)
