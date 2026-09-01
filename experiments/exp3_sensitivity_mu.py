"""Expérience 3 : analyse de sensibilité du paramètre de pénalisation µ.

Responsable : M5, interprétation avec M4.
Dépend de : la dérivation de M4 sur le comportement asymptotique en µ.

Satisfait l'exigence (v) de la Contrainte méthodologique 3 : analyse de
sensibilité d'au moins un hyperparamètre. L'oublier est listé en section 14
parmi les erreurs à éviter.

    Objectif    Mesurer le compromis porté par µ.
    Paramètres  µ ∈ {1, 10, 100, 1000}.
    Données     Réseau synthétique, demande moyenne.
    Méthode     Résoudre le problème pénalisé pour chaque µ, observer
                convergence et violation résiduelle.
    Métriques   ‖Aq − b‖ finale, nombre d'itérations avant convergence,
                conditionnement effectif de 2C + 2µAᵀA.
    Attendu     La violation résiduelle décroît avec µ, mais la convergence
                ralentit quand µ devient grand.
    Graphique   Courbes de convergence superposées, une par µ.

Le compromis à expliciter, en lien direct avec la dérivation de l'Étape 7 :
augmenter µ resserre la contrainte d'égalité, mais alourdit la plus grande
valeur propre de la hessienne, donc dégrade κ(H), donc impose un pas plus petit
via η < 2/L, donc ralentit la convergence. Les deux effets ont la même origine
algébrique. Ce n'est pas une coïncidence expérimentale, et le rapport doit le
dire ainsi.

Attention au protocole : si η est recalculé à partir de 2/L pour chaque µ, le
nombre d'itérations mélange deux effets. Fixer le protocole retenu et le
documenter, sans quoi la courbe n'est pas interprétable.
"""

from __future__ import annotations

import csv

import _bootstrap  # noqa: F401
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from data.generate_network import charger_reseau
from src.graph.build_graph import (
    construire_matrice_incidence,
    construire_second_membre,
    vecteur_couts,
)
from src.optimization.gradient_descent import descente_projetee, pas_maximal_theorique
from src.optimization.objective import cout, hessienne, violation_contrainte
from src.probability.demand_model import parametres_demande

VALEURS_DE_MU = (1.0, 10.0, 100.0, 1000.0)
TOLERANCE = 1e-8
MAX_ITERATIONS = 200_000


def main() -> None:
    reseau = charger_reseau(_bootstrap.CONFIG)
    A = construire_matrice_incidence(reseau)
    couts = vecteur_couts(reseau)
    mu_demande, _ = parametres_demande(reseau)
    b = construire_second_membre(reseau, mu_demande)

    lignes = []
    historiques = {}

    for mu in VALEURS_DE_MU:
        H = hessienne(A, couts, mu)
        valeurs_propres = np.linalg.eigvalsh(H)
        pas_max = pas_maximal_theorique(A, couts, mu)

        # Protocole retenu : le pas est recalculé pour chaque µ, à la moitié de la
        # borne. Le nombre d'itérations mélange donc deux effets, le durcissement
        # du problème et le rétrécissement du pas. Ils ont la même origine, la
        # matrice 2C + 2µAᵀA, et c'est précisément le compromis qu'on mesure.
        q, historique = descente_projetee(
            A, b, couts, mu, tolerance=TOLERANCE, max_iterations=MAX_ITERATIONS
        )
        historiques[mu] = historique

        lignes.append(
            {
                "mu": mu,
                "L": valeurs_propres.max(),
                "conditionnement_H": valeurs_propres.max() / valeurs_propres.min(),
                "pas_maximal_2_sur_L": pas_max,
                "pas_utilise": 0.5 * pas_max,
                "iterations": historique.n_iterations,
                "a_converge": historique.a_converge,
                "cout_technique": cout(q, couts),
                "violation_residuelle": violation_contrainte(q, A, b),
            }
        )
        print(
            f"  mu={mu:7.0f}  L={valeurs_propres.max():10.2f}  "
            f"pas={0.5 * pas_max:.2e}  iterations={historique.n_iterations:6d}  "
            f"violation={violation_contrainte(q, A, b):9.5f}"
        )

    chemin_table = _bootstrap.TABLEAUX / "exp3_sensibilite_mu.csv"
    with open(chemin_table, "w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
        redacteur.writeheader()
        redacteur.writerows(lignes)
    print(f" -> tableau : {chemin_table}")

    figure, (gauche, droite) = plt.subplots(1, 2, figsize=(13, 5))

    for mu, historique in historiques.items():
        gauche.semilogy(historique.valeurs_objectif, label=f"µ = {mu:g}")
    gauche.set_xlabel("itération k")
    gauche.set_ylabel("J(q_k), échelle logarithmique")
    gauche.set_title("Convergence selon µ")
    gauche.set_xscale("log")
    gauche.grid(True, linestyle="--", alpha=0.5)
    gauche.legend()

    mus = [ligne["mu"] for ligne in lignes]
    droite.loglog(mus, [ligne["violation_residuelle"] for ligne in lignes],
                  "o-", label="violation résiduelle ‖Aq − b‖")
    droite.loglog(mus, [ligne["iterations"] for ligne in lignes],
                  "s--", label="itérations jusqu'à convergence")
    droite.set_xlabel("µ")
    droite.set_title("Le compromis : précision contre vitesse")
    droite.grid(True, which="both", linestyle="--", alpha=0.5)
    droite.legend()

    figure.suptitle(
        "Expérience 3 : sensibilité au paramètre de pénalisation µ", fontweight="bold"
    )
    figure.tight_layout()
    chemin_figure = _bootstrap.FIGURES / "exp3_sensibilite_mu.png"
    figure.savefig(chemin_figure, dpi=200)
    plt.close(figure)
    print(f" -> figure  : {chemin_figure}")


if __name__ == "__main__":
    main()
