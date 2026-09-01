"""Expérience 5 : effet du maillage du réseau sur le conditionnement.

Responsable : M5, interprétation avec M2.
Dépend de : ``generer_variantes_de_maillage`` (M1/M2) et l'analyse de l'Étape 3.

Seconde confrontation théorie/expérience exigée par le sujet. Elle valide
l'affirmation centrale du volet algèbre linéaire : un réseau mal maillé se
traduit directement par une instabilité numérique de la résolution.

    Objectif    Vérifier empiriquement le lien entre structure du graphe et
                stabilité numérique établi à l'Étape 3.
    Paramètres  Plusieurs variantes du réseau, de l'arbre couvrant au réseau
                bien maillé.
    Données     Réseaux synthétiques à densités de connexion différentes.
    Méthode     Calculer κ pour chaque variante, résoudre et compter les
                itérations nécessaires.
    Métriques   Conditionnement, nombre d'itérations à convergence.
    Attendu     Un réseau mal maillé a un conditionnement plus élevé et
                nécessite davantage d'itérations.
    Graphique   Conditionnement en fonction du nombre de conduites, ou
                itérations en fonction du conditionnement.

Conditions de validité du protocole, à tenir sous peine de comparer des choses
différentes :

- toutes les variantes doivent rester connexes, sinon le rang de A change de
  nature et les κ ne sont plus comparables ;
- µ, η et la tolérance doivent être identiques d'une variante à l'autre ;
- si η est dérivé de 2/L, il change *mécaniquement* avec le conditionnement.
  Deux protocoles se défendent (η fixe pour tous, ou η adapté à chaque
  variante), mais ils ne mesurent pas la même chose, et le rapport doit dire
  lequel est retenu et pourquoi.

Le résultat attendu est une relation croissante, pas une droite : ne pas
sur-interpréter une régression linéaire sur cinq points.
"""

from __future__ import annotations

import csv

import _bootstrap  # noqa: F401
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from data.generate_network import charger_reseau, generer_variantes_de_maillage
from src.graph.build_graph import (
    construire_graphe,
    construire_matrice_incidence,
    construire_second_membre,
    vecteur_couts,
)
from src.graph import graph_analysis as ga
from src.optimization.gradient_descent import descente_projetee, pas_maximal_theorique
from src.optimization.objective import hessienne
from src.probability.demand_model import parametres_demande

DENSITES = (0.0, 0.25, 0.5, 0.75, 1.0)
MU = 100.0
TOLERANCE = 1e-8
MAX_ITERATIONS = 200_000


def conditionnement_hessienne(A: np.ndarray, couts: np.ndarray, mu: float) -> float:
    """Rapport entre la plus grande et la plus petite valeur propre de 2C + 2µAᵀA.

    C'est cette quantité, et non κ(A), qui gouverne la vitesse de la descente de
    gradient. Voir la section 6.3 du document du Membre 4.
    """
    valeurs_propres = np.linalg.eigvalsh(hessienne(A, couts, mu))
    return float(valeurs_propres.max() / valeurs_propres.min())


def main() -> None:
    reseau = charger_reseau(_bootstrap.CONFIG)
    mu_demande, _ = parametres_demande(reseau)
    variantes = generer_variantes_de_maillage(reseau, DENSITES)

    # Protocole : un pas identique pour toutes les variantes, choisi comme la
    # moitié de la plus petite borne rencontrée. Un pas recalculé pour chaque
    # variante changerait mécaniquement avec le conditionnement et mélangerait
    # les deux effets qu'on cherche justement à séparer.
    bornes = [
        pas_maximal_theorique(
            construire_matrice_incidence(variante), vecteur_couts(variante), MU
        )
        for variante in variantes.values()
    ]
    eta_commun = 0.5 * min(bornes)
    print(f"  pas commun à toutes les variantes : {eta_commun:.3e}")

    lignes = []

    for densite in sorted(variantes):
        variante = variantes[densite]
        A = construire_matrice_incidence(variante)
        couts = vecteur_couts(variante)
        graphe = construire_graphe(variante)
        b = construire_second_membre(variante, mu_demande)

        _, historique = descente_projetee(
            A, b, couts, MU, eta=eta_commun,
            tolerance=TOLERANCE, max_iterations=MAX_ITERATIONS,
        )

        lignes.append(
            {
                "densite": densite,
                "n_conduites": len(variante.conduites),
                "connexe": ga.est_connexe(graphe),
                "rang_A": ga.rang(A),
                "dimension_noyau": len(variante.conduites) - ga.rang(A),
                "conditionnement_A": ga.conditionnement(A),
                "conditionnement_H": conditionnement_hessienne(A, couts, MU),
                "iterations": historique.n_iterations,
                "a_converge": historique.a_converge,
            }
        )
        print(
            f"  densité {densite:4.2f} : {len(variante.conduites):2d} conduites, "
            f"{len(variante.conduites) - ga.rang(A)} boucle(s)  "
            f"κ(A)={ga.conditionnement(A):6.3f}  "
            f"κ(H)={conditionnement_hessienne(A, couts, MU):8.1f}  "
            f"itérations={historique.n_iterations:6d}"
        )

    chemin_table = _bootstrap.TABLEAUX / "exp5_maillage_conditionnement.csv"
    with open(chemin_table, "w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
        redacteur.writeheader()
        redacteur.writerows(lignes)
    print(f" -> tableau : {chemin_table}")

    conduites = [ligne["n_conduites"] for ligne in lignes]
    boucles = [ligne["dimension_noyau"] for ligne in lignes]
    kappas_A = [ligne["conditionnement_A"] for ligne in lignes]
    kappas_H = [ligne["conditionnement_H"] for ligne in lignes]
    iterations = [ligne["iterations"] for ligne in lignes]

    figure, (gauche, droite) = plt.subplots(1, 2, figsize=(13, 5))

    gauche.plot(conduites, kappas_A, "o-", label="κ(A), résolution de Aq = b")
    gauche.set_xlabel("nombre de conduites")
    gauche.set_ylabel("κ(A)", color="tab:blue")
    gauche.tick_params(axis="y", labelcolor="tab:blue")
    gauche.grid(True, linestyle="--", alpha=0.5)

    jumeau = gauche.twinx()
    jumeau.plot(conduites, kappas_H, "s--", color="tab:red",
                label="κ(H), vitesse de la descente")
    jumeau.set_ylabel("κ(2C + 2µAᵀA)", color="tab:red")
    jumeau.tick_params(axis="y", labelcolor="tab:red")
    gauche.set_title("Deux conditionnements, deux tendances opposées")

    droite.plot(kappas_H, iterations, "s", color="tab:red")
    for kappa, iteration, n_boucles in zip(kappas_H, iterations, boucles):
        droite.annotate(f"{n_boucles} boucle(s)", (kappa, iteration),
                        textcoords="offset points", xytext=(6, 4), fontsize=8)
    droite.set_xlabel("κ(H) = κ(2C + 2µAᵀA)")
    droite.set_ylabel("itérations jusqu'à convergence")
    droite.set_title("C'est κ(H) qui prédit le nombre d'itérations")
    droite.grid(True, linestyle="--", alpha=0.5)

    figure.suptitle(
        "Expérience 5 : maillage du réseau, conditionnement et coût du calcul",
        fontweight="bold",
    )
    figure.tight_layout()
    chemin_figure = _bootstrap.FIGURES / "exp5_maillage_conditionnement.png"
    figure.savefig(chemin_figure, dpi=200)
    plt.close(figure)
    print(f" -> figure  : {chemin_figure}")


if __name__ == "__main__":
    main()
