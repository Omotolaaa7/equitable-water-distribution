"""Expérience 4 : vérification empirique de la borne de convergence.

Responsable : M5, interprétation avec M4.
Dépend de : la borne théorique η < 2/L établie par M4 à partir du L de M2.

Première des deux confrontations théorie/expérience exigées par le sujet.

    Objectif    Confronter la borne théorique sur le pas au comportement
                réellement observé.
    Paramètres  Plusieurs η, certains sous 2/L, d'autres au-delà.
    Données     Réseau synthétique.
    Méthode     Lancer la descente projetée pour chaque η, suivre la norme du
                gradient et J(q_k) au fil des itérations.
    Métriques   ‖∇J(q_k)‖ et J(q_k) en fonction de k.
    Attendu     Convergence stable sous la borne, oscillation ou divergence
                au-delà.
    Graphique   Courbes de J(q_k) en fonction de k, une par η.

Protocole recommandé : encadrer franchement le seuil, par exemple
η ∈ {0.1, 0.5, 0.9, 1.1, 1.5} × (2/L). Un balayage qui reste entièrement d'un
côté du seuil ne démontre rien.

Deux précautions de mise en œuvre :

- prévoir un garde-fou de dépassement numérique. Au-delà de 2/L, J(q_k) part en
  overflow en quelques dizaines d'itérations, et le script doit s'arrêter
  proprement plutôt que de remplir la sortie de ``inf`` et de ``nan`` ;
- tracer J en échelle logarithmique. Sur une échelle linéaire, les cas
  divergents écrasent visuellement les cas convergents et la figure ne montre
  plus rien.

L'erreur à ne pas commettre, listée en section 14 : présenter une courbe qui
descend comme preuve de convergence. Ce qui est démontré ici, c'est le lien
entre la constante de Lipschitz calculée à l'Étape 3 et le comportement
observé de part et d'autre du seuil, et non le simple fait que ça descende.
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
from src.probability.demand_model import parametres_demande

MU = 100.0
# Le balayage encadre franchement le seuil : trois pas en dessous, deux au-dessus.
# Un balayage entièrement d'un côté ne démontrerait rien.
FACTEURS = (0.1, 0.5, 0.9, 1.1, 1.5)
MAX_ITERATIONS = 60_000


def main() -> None:
    reseau = charger_reseau(_bootstrap.CONFIG)
    A = construire_matrice_incidence(reseau)
    couts = vecteur_couts(reseau)
    mu_demande, _ = parametres_demande(reseau)
    b = construire_second_membre(reseau, mu_demande)

    borne = pas_maximal_theorique(A, couts, MU)
    L = 2.0 / borne
    print(f"  L = {L:.3f}, borne théorique 2/L = {borne:.6f}")

    lignes = []
    historiques = {}

    for facteur in FACTEURS:
        eta = facteur * borne
        _, historique = descente_projetee(
            A, b, couts, MU, eta=eta, max_iterations=MAX_ITERATIONS
        )
        historiques[facteur] = historique

        valeurs = np.array(historique.valeurs_objectif)
        remontee_max = float(np.max(np.diff(valeurs))) if valeurs.size > 1 else 0.0

        lignes.append(
            {
                "facteur_de_la_borne": facteur,
                "eta": eta,
                "sous_la_borne": facteur < 1.0,
                "a_converge": historique.a_converge,
                "iterations": historique.n_iterations,
                "motif_arret": historique.motif_arret,
                "J_final": valeurs[-1],
                "remontee_maximale_de_J": remontee_max,
            }
        )
        print(
            f"  eta = {facteur:4.1f} x 2/L = {eta:.2e}  "
            f"converge={str(historique.a_converge):5s}  "
            f"iterations={historique.n_iterations:6d}  "
            f"remontée max de J = {remontee_max:.3e}"
        )

    chemin_table = _bootstrap.TABLEAUX / "exp4_convergence.csv"
    with open(chemin_table, "w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
        redacteur.writeheader()
        redacteur.writerows(lignes)
    print(f" -> tableau : {chemin_table}")

    figure, axes = plt.subplots(figsize=(10, 6))
    for facteur, historique in historiques.items():
        style = "-" if facteur < 1.0 else "--"
        axes.semilogy(
            historique.valeurs_objectif[:2000],
            style,
            label=f"η = {facteur:g} × 2/L" + ("" if facteur < 1.0 else "  (au-delà du seuil)"),
        )

    axes.set_xlabel("itération k")
    axes.set_ylabel("J(q_k), échelle logarithmique")
    axes.set_title(
        f"Expérience 4 : la borne η < 2/L ≈ {borne:.4f}, confrontée à l'expérience",
        fontweight="bold",
    )
    axes.grid(True, which="both", linestyle="--", alpha=0.5)
    axes.legend()

    figure.tight_layout()
    chemin_figure = _bootstrap.FIGURES / "exp4_convergence.png"
    figure.savefig(chemin_figure, dpi=200)
    plt.close(figure)
    print(f" -> figure  : {chemin_figure}")


if __name__ == "__main__":
    main()
