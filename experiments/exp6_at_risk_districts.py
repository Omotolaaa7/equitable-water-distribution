"""Expérience 6 : identification des quartiers à risque.

Responsable : M3, avec M5 pour l'exécution.
Dépend de : les estimateurs et intervalles de confiance de l'Étape 4.

Exploite le volet statistique pour enrichir l'interprétation. C'est
l'expérience qui relie le travail probabiliste au terrain : elle produit
l'information qu'un ingénieur réseau peut réellement utiliser.

    Objectif    Repérer les quartiers dont la demande s'écarte régulièrement
                des prévisions.
    Paramètres  Historique simulé de demande sur plusieurs périodes.
    Données     Tirages répétés avec un biais volontaire sur certains quartiers.
    Méthode     Calcul d'intervalles de confiance et de corrélations,
                comparaison à la demande prévue.
    Métriques   Fréquence de dépassement de l'IC par quartier.
    Attendu     Identification des quartiers à demande atypique.
    Graphique   Tableau récapitulatif par quartier.

Point de méthode à ne pas manquer : le biais est introduit *volontairement* sur
certains quartiers. Ce sont eux la vérité terrain de l'expérience, et le
critère de réussite est que la méthode les retrouve, sans lever de fausse
alerte sur les quartiers non biaisés. Le taux de fausses alertes attendu sur un
IC à 95 % est d'environ 5 % : c'est le repère par rapport auquel toute
fréquence mesurée doit être lue.

Interprétation à faire, et qui est le vrai intérêt de l'expérience : relier ces
quartiers à la robustesse de q*. Un quartier à demande atypique *et* situé en
bout de réseau, relié par une seule conduite, cumule un risque statistique et
un risque structurel. C'est le point où le volet probabiliste et le volet
graphe se rejoignent, et c'est le genre de synthèse que la grille récompense.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M3 avec M5, Expérience 6.")


if __name__ == "__main__":
    main()
=======
"""
Expérience 6 : Analyse des Quartiers à Risque et Génération des Figures du Rapport
Auteur : Membre 3 (Probabilités et Statistiques)
Projet : Distribution d'eau équitable sous incertitude (Thème 3)

Ce script (Étape 4) :
1. Importe le modèle probabiliste validé (src.probability.demand_model).
2. Réalise l'analyse de risque stochastique et topologique (Expérience 6).
3. Génère et enregistre les 4 figures scientifiques dans results/figures/.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Ajout du chemin racine pour permettre l'import de src.probability
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.probability.demand_model import DemandModel


def run_experiment_6():
    print("=" * 95)
    print("      EXPÉRIENCE 6 : ANALYSE DES QUARTIERS À RISQUE ET PRODUCTION DES FIGURES")
    print("=" * 95)

    # 1. Dossier de sauvegarde des figures
    dossier_figures = os.path.join("results", "figures")
    os.makedirs(dossier_figures, exist_ok=True)

    # 2. Instanciation du modèle (Membre 3)
    model = DemandModel()
    quartiers = model.quartiers
    n = model.n_districts

    # 3. Simulation de 10 000 tirages pour analyse de risque
    np.random.seed(42)
    N_sim = 10000
    samples = model.sample_demands(n_samples=N_sim, seed=42)

    # Calcul des quantiles de risque
    q95 = np.percentile(samples, 95, axis=0)
    q99 = np.percentile(samples, 99, axis=0)
    max_obs = np.max(samples, axis=0)

    print("\n1. ANALYSE STATISTIQUE DES RISQUES PAR QUARTIER (EXPÉRIENCE 6) :")
    print("-" * 95)
    print(
        f"{'Quartier':<10}{'mu (m3/h)':<12}{'sigma':<10}{'Quantile 95%':<16}{'Quantile 99%':<16}{'Pic Max Observé':<18}{'Type de Risque':<20}")
    print("-" * 95)
    for i, q in enumerate(quartiers):
        if q == "Q1":
            type_risque = "Topologique (Pont unique)"
        elif q == "Q6":
            type_risque = "Stochastique (Forte variance)"
        elif q in ["Q4", "Q5"]:
            type_risque = "Transit inter-zones"
        else:
            type_risque = "Modéré / Standard"
        print(
            f"{q:<10}{model.mu[i]:<12.2f}{model.sigma[i]:<10.2f}{q95[i]:<16.2f}{q99[i]:<16.2f}{max_obs[i]:<18.2f}{type_risque:<20}")
    print("-" * 95)

    print("\n2. GÉNÉRATION DES FIGURES HAUTE DÉFINITION DANS 'results/figures/' :")

    # -------------------------------------------------------------
    # Figure 1 : Matrice de Corrélation R et Matrice de Covariance Sigma
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    im1 = axes[0].imshow(model.R, cmap="Blues", vmin=0, vmax=1)
    axes[0].set_title(r"Matrice de Corrélation Spatiale $R$", fontsize=13, fontweight='bold')
    axes[0].set_xticks(range(n))
    axes[0].set_yticks(range(n))
    axes[0].set_xticklabels(quartiers)
    axes[0].set_yticklabels(quartiers)
    for i in range(n):
        for j in range(n):
            axes[0].text(j, i, f"{model.R[i, j]:.2f}", ha="center", va="center",
                         color="black" if model.R[i, j] < 0.6 else "white")
    fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

    im2 = axes[1].imshow(model.Sigma, cmap="YlOrRd")
    axes[1].set_title(r"Matrice de Covariance $\Sigma$ ($m^6/h^2$)", fontsize=13, fontweight='bold')
    axes[1].set_xticks(range(n))
    axes[1].set_yticks(range(n))
    axes[1].set_xticklabels(quartiers)
    axes[1].set_yticklabels(quartiers)
    for i in range(n):
        for j in range(n):
            axes[1].text(j, i, f"{model.Sigma[i, j]:.1f}", ha="center", va="center",
                         color="black" if model.Sigma[i, j] < 50 else "white", fontsize=9)
    fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

    plt.tight_layout()
    f1_path = os.path.join(dossier_figures, "fig1_matrices_correlation_covariance.png")
    plt.savefig(f1_path, dpi=300)
    plt.close()
    print(f" -> Figure 1 sauvegardée : {f1_path}")

    # -------------------------------------------------------------
    # Figure 2 : Densités de Probabilité Gaussiennes par Quartier
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x_axis = np.linspace(5, 85, 500)
    for i, q in enumerate(quartiers):
        pdf = stats.norm.pdf(x_axis, loc=model.mu[i], scale=model.sigma[i])
        ax.plot(x_axis, pdf, label=rf"{q} ($\mu={model.mu[i]:.0f}, \sigma={model.sigma[i]:.0f}$)", lw=2)
    ax.set_title("Distributions de Probabilité Gaussiens de la Demande par Quartier", fontsize=13, fontweight='bold')
    ax.set_xlabel(r"Demande en eau ($m^3/h$)", fontsize=11)
    ax.set_ylabel("Densité de probabilité", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    f2_path = os.path.join(dossier_figures, "fig2_densites_probabilites_demande.png")
    plt.savefig(f2_path, dpi=300)
    plt.close()
    print(f" -> Figure 2 sauvegardée : {f2_path}")

    # -------------------------------------------------------------
    # Figure 3 : Preuve de Vitesse de Convergence en 1/sqrt(N) (Échelle Log-Log)
    # -------------------------------------------------------------
    tailles_N = np.array([10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 50000])
    erreurs = []
    for N_k in tailles_N:
        tir = model.sample_demands(n_samples=N_k, seed=42)
        erreurs.append(np.linalg.norm(np.mean(tir, axis=0) - model.mu, 2))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(tailles_N, erreurs, 'o-', color='navy', lw=2, label=r"Erreur empirique $\|\hat{\mu}_N - \mu\|_2$")
    ax.loglog(tailles_N, erreurs[0] * np.sqrt(tailles_N[0]) / np.sqrt(tailles_N), '--', color='crimson', lw=2,
              label=r"Pente théorique $O(1/\sqrt{N})$")
    ax.set_title("Vérification de la Vitesse de Convergence Monte-Carlo (Échelle Log-Log)", fontsize=13,
                 fontweight='bold')
    ax.set_xlabel(r"Nombre de tirages $N$", fontsize=11)
    ax.set_ylabel(r"Erreur euclidienne $\|\hat{\mu}_N - \mu\|_2$", fontsize=11)
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend(fontsize=11)

    plt.tight_layout()
    f3_path = os.path.join(dossier_figures, "fig3_convergence_loi_grands_nombres.png")
    plt.savefig(f3_path, dpi=300)
    plt.close()
    print(f" -> Figure 3 sauvegardée : {f3_path}")

    # -------------------------------------------------------------
    # Figure 4 : Profils de Risque et Boxplots (Dispersion et Dépassements)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5))
    box = ax.boxplot([samples[:, i] for i in range(n)], patch_artist=True, showmeans=True)
    ax.set_xticks(range(1, n + 1))
    ax.set_xticklabels(quartiers)
    for patch in box['boxes']:
        patch.set_facecolor('#a6c8e0')
    ax.axhline(60, color='red', linestyle='--', label='Seuil de charge critique locale (60 m3/h)')
    ax.set_title("Profil de Risque et Dispersion de la Demande par Quartier (Expérience 6)", fontsize=13,
                 fontweight='bold')
    ax.set_ylabel(r"Demande instantanée ($m^3/h$)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    plt.tight_layout()
    f4_path = os.path.join(dossier_figures, "fig4_profil_risque_quartiers.png")
    plt.savefig(f4_path, dpi=300)
    plt.close()
    print(f" -> Figure 4 sauvegardée : {f4_path}")

    print("\n" + "=" * 95)
    print(">>> EXPÉRIENCE 6 ET FIGURES TERMINÉES AVEC SUCCÈS ! <<<")
    print("=" * 95)


if __name__ == "__main__":
    run_experiment_6()
>>>>>>> 9ede8c2 (Probabilité: libvrable membre 3)
