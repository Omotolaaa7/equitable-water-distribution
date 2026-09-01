"""Descente de gradient projetée sur l'orthant positif.

Responsable : M5 pour l'implémentation, à partir des dérivations de M4.
Source des formules : docs/section_optimisation_membre4.pdf, rédigé par
Aïchatou Traoré. Les numéros de section cités ci-dessous renvoient à ce document.
Dépend de : ``objective`` (Étape 8) et du conditionnement calculé par M2.
Étape 9 du pipeline.

Attention : ne rien coder ici avant que les huit points du jalon (section 16
du plan) soient cochés.

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
   la séparabilité de l'orthant positif qui rend la projection aussi simple.
   Elle ne le serait pas sur un ensemble couplant les composantes, comme les
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

from .objective import gradient, hessienne, objectif, violation_contrainte

# Au-dela de ce deplacement en une iteration, la descente a divergé. Le seuil
# n'est pas dans le document du Membre 4 : il sert de garde-fou a l'Experience 4,
# qui fait exprès de dépasser la borne 2/L et remplirait sinon la sortie de inf
# et de nan avant le nombre maximal d'itérations.
SEUIL_DIVERGENCE = 1e12


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
    return np.maximum(np.asarray(q, dtype=float), 0.0)


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
    # H est symétrique : eigvalsh, jamais eigvals, qui renverrait des valeurs
    # complexes à partie imaginaire numérique et rendrait la comparaison bancale.
    L = float(np.linalg.eigvalsh(hessienne(A, couts, mu)).max())
    return 2.0 / L


def descente_projetee(
    A: np.ndarray,
    b: np.ndarray,
    couts: np.ndarray,
    mu: float,
    eta: float | None = None,
    q_initial: np.ndarray | None = None,
    tolerance: float = 1e-8,
    max_iterations: int = 10_000,
    critere: str = "deplacement",
) -> tuple[np.ndarray, HistoriqueConvergence]:
    """Résout le problème pénalisé par descente de gradient projetée.

    Args:
        A: matrice d'incidence, forme (|V|, |E|).
        b: second membre de conservation, longueur |V|.
        couts: vecteur des c_e, longueur |E|.
        mu: paramètre de pénalisation.
        eta: pas d'apprentissage. Si ``None``, prendre une fraction de la borne
            théorique, mais alors le *dire* dans le rapport, et non laisser
            croire que le pas a été réglé à la main.
        q_initial: point de départ. Par défaut le vecteur nul, qui est
            admissible pour q ≥ 0.
        tolerance: seuil d'arrêt sur ‖q_{k+1} − q_k‖.
        max_iterations: garde-fou contre une divergence, utile précisément
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

    Écart assumé avec le document du Membre 4. Sa section 5.3 propose trois
    critères, et son pseudo-code retient la norme du gradient. Sur un problème
    projeté, ce critère peut ne jamais être atteint : une conduite dont le débit
    optimal vaut zéro garde un gradient non nul, que la projection annule à
    chaque tour. La boucle irait alors jusqu'à max_iterations sans que rien ne
    signale d'anomalie.

    Les trois critères de M4 sont donc tous disponibles via ``critere``, et le
    déplacement est retenu par défaut. À signaler au Membre 4 pour qu'il tranche
    et harmonise le rapport avec le code.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    couts = np.asarray(couts, dtype=float)

    if critere not in {"deplacement", "gradient", "cout"}:
        raise ValueError(
            f"Critère d'arrêt inconnu : {critere!r}. Attendu 'deplacement', "
            "'gradient' ou 'cout'."
        )

    if eta is None:
        # Moitié de la borne théorique, soit 1/L. Dans la zone stable et loin du
        # seuil, conformément à la section 5.2 du document du Membre 4. Ce choix
        # doit être signalé dans le rapport plutôt que passé sous silence.
        eta = 0.5 * pas_maximal_theorique(A, couts, mu)

    if q_initial is None:
        q = np.zeros(A.shape[1], dtype=float)
    else:
        q = projeter_orthant_positif(q_initial)

    historique = HistoriqueConvergence()
    cout_precedent = objectif(q, A, b, couts, mu)

    for k in range(max_iterations):
        g = gradient(q, A, b, couts, mu)
        valeur = objectif(q, A, b, couts, mu)

        historique.valeurs_objectif.append(valeur)
        historique.normes_gradient.append(float(np.linalg.norm(g)))
        historique.violations_contrainte.append(violation_contrainte(q, A, b))
        historique.n_iterations = k + 1

        # Mise à jour puis projection, à chaque itération (section 4.3 de M4).
        q_suivant = projeter_orthant_positif(q - eta * g)
        deplacement = float(np.linalg.norm(q_suivant - q))

        if not np.isfinite(deplacement) or deplacement > SEUIL_DIVERGENCE:
            historique.a_converge = False
            historique.motif_arret = f"divergence détectée à l'itération {k + 1}"
            return q_suivant, historique

        q = q_suivant

        if critere == "deplacement":
            atteint = deplacement < tolerance
        elif critere == "gradient":
            atteint = historique.normes_gradient[-1] < tolerance
        else:
            valeur_suivante = objectif(q, A, b, couts, mu)
            atteint = abs(valeur_suivante - cout_precedent) < tolerance
            cout_precedent = valeur_suivante

        if atteint:
            historique.a_converge = True
            historique.motif_arret = f"critère '{critere}' atteint, seuil {tolerance:g}"
            return q, historique

    historique.a_converge = False
    historique.motif_arret = f"nombre maximal d'itérations atteint ({max_iterations})"
    return q, historique
