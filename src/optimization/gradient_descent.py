"""Descente de gradient projetée sur l'orthant positif.

Responsable : M5 pour l'implémentation, à partir des dérivations de M4.
Dépend de : ``objective`` (Étape 8) et du conditionnement calculé par M2.
Étape 9 du pipeline.

⚠ Ne rien coder ici avant que les huit points du jalon (section 16 du plan)
soient cochés.

---------------------------------------------------------------------------
L'algorithme, tel qu'il doit figurer en pseudo-code dans le rapport

    Entrées : A, b, c, µ, η, q_0, tolérance, k_max
    Pour k = 0, 1, 2, … :
        g_k     ← ∇J(q_k) = 2Cq_k + 2µAᵀ(Aq_k − b)
        q_{k+1} ← P( q_k − η g_k )        avec  P(x) = max(x, 0)
        arrêt si ‖q_{k+1} − q_k‖ < tolérance  ou  k = k_max
    Sortie : q_k

Deux points que le rapport doit justifier, pas seulement énoncer :

1. **Pourquoi max(·, 0) est la projection euclidienne sur {q ≥ 0}.** Le
   problème min_{y ≥ 0} ‖y − x‖² se sépare composante par composante : chaque
   min_{y_e ≥ 0} (y_e − x_e)² est atteint en x_e si x_e ≥ 0, en 0 sinon. C'est
   la séparabilité de l'orthant positif qui rend la projection aussi simple —
   elle ne le serait pas sur un ensemble couplant les composantes, comme les
   contraintes de capacité q_e ≤ cap_e si le groupe décidait de les activer.

2. **Pourquoi η < 2/L garantit la convergence**, avec L = λ_max(2C + 2µAᵀA).
   Résultat classique de la descente de gradient projetée sur fonction convexe
   à gradient L-lipschitzien. La borne est *théorique* : l'Expérience 4 la
   confronte au comportement observé de part et d'autre du seuil.

Erreur à ne pas commettre, listée en section 14 du plan : projeter une seule
fois à la fin plutôt qu'à chaque itération. Ce n'est pas une optimisation de
code, c'est un autre algorithme, qui ne converge pas vers le même point.
---------------------------------------------------------------------------
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class HistoriqueConvergence:
    """Trace de la descente, pour les Expériences 3, 4 et 5.

    Ces listes ne servent pas au calcul : elles servent aux figures et à la
    confrontation théorie/expérience. Les enregistrer pendant la descente évite
    d'avoir à relancer l'optimisation pour tracer une courbe.
    """

    valeurs_objectif: list[float] = field(default_factory=list)
    normes_gradient: list[float] = field(default_factory=list)
    violations_contrainte: list[float] = field(default_factory=list)
    n_iterations: int = 0
    a_converge: bool = False
    motif_arret: str = ""


def projeter_orthant_positif(q: np.ndarray) -> np.ndarray:
    """Projection euclidienne sur {q ≥ 0}, composante par composante.

    P(q)_e = max(q_e, 0)

    Fonction d'une ligne, isolée volontairement : c'est le seul endroit du code
    où la contrainte de positivité est appliquée, elle est testable seule
    (``tests/test_projection.py``), et sa justification mathématique figure dans
    le docstring du module.
    """
    raise NotImplementedError("M5 à partir de M4 — Étape 9.")


def pas_maximal_theorique(A: np.ndarray, couts: np.ndarray, mu: float) -> float:
    """Borne théorique sur le pas d'apprentissage : 2/L.

    Avec L = λ_max(2C + 2µAᵀA), calculée par
    ``src.graph.graph_analysis.constante_de_lipschitz``.

    Choisir η arbitrairement sans passer par cette borne est explicitement
    listé comme erreur à éviter : cela rend toute l'analyse de convergence
    invérifiable. Une valeur usuelle en pratique est η = 1/L, dans la zone
    stable et loin du seuil.

    Returns:
        La borne 2/L, au-delà de laquelle la théorie ne garantit plus rien.
    """
    raise NotImplementedError("M5 à partir de M4 et M2 — Étape 9.")


def descente_projetee(
    A: np.ndarray,
    b: np.ndarray,
    couts: np.ndarray,
    mu: float,
    eta: float | None = None,
    q_initial: np.ndarray | None = None,
    tolerance: float = 1e-8,
    max_iterations: int = 10_000,
) -> tuple[np.ndarray, HistoriqueConvergence]:
    """Résout le problème pénalisé par descente de gradient projetée.

    Args:
        A: matrice d'incidence, forme (|V|, |E|).
        b: second membre de conservation, longueur |V|.
        couts: vecteur des c_e, longueur |E|.
        mu: paramètre de pénalisation.
        eta: pas d'apprentissage. Si ``None``, prendre une fraction de la borne
            théorique — mais alors le *dire* dans le rapport, et non laisser
            croire que le pas a été réglé à la main.
        q_initial: point de départ. Par défaut le vecteur nul, qui est
            admissible pour q ≥ 0.
        tolerance: seuil d'arrêt sur ‖q_{k+1} − q_k‖.
        max_iterations: garde-fou contre une divergence — utile précisément
            dans l'Expérience 4, où l'on fait *exprès* de dépasser 2/L.

    Returns:
        Le couple (q*, historique).

    Note sur le critère d'arrêt : sur un problème contraint, ‖∇J‖ → 0 n'est pas
    le bon critère, puisqu'à l'optimum les composantes actives de la contrainte
    ont un gradient non nul, poussant vers l'extérieur de l'orthant. Le critère
    correct porte sur le déplacement ‖q_{k+1} − q_k‖, qui capte le point fixe de
    l'itération projetée. C'est un point à justifier explicitement dans le
    rapport : c'est exactement le genre de subtilité que la rubrique
    « Optimisation » évalue.
    """
    raise NotImplementedError(
        "M5 à partir des dérivations validées et relues de M4 — Étape 9. "
        "Livrable : algorithme validé sur un petit cas test dont la solution "
        "est vérifiable à la main, avant utilisation sur le réseau complet."
    )
