"""Fonction de coût pénalisée J(q) et son gradient ∇J(q).

Responsable : M5 pour l'implémentation, à partir des dérivations de M4.
Dépend de : les Étapes 6, 7 et 8 (formulation, pénalisation, gradient).
Alimente : ``gradient_descent`` et toutes les expériences.

⚠ Ne rien coder ici avant que la dérivation de M4 soit écrite et relue par
deux autres membres. Voir le jalon, section 16 du plan.

---------------------------------------------------------------------------
Le contenu mathématique que ce module implémente

Problème d'origine (Étape 6) :

    q* = argmin_q  Σ_{e∈E} c_e q_e²      sous  Aq = b,  q ≥ 0

Convexité (à démontrer, Étape 6) : Σ c_e q_e² = qᵀCq avec C = diag(c_e). C est
diagonale à coefficients strictement positifs, donc définie positive, donc la
forme quadratique est strictement convexe. La stricte positivité des c_e n'est
pas un détail d'hygiène : c'est l'hypothèse exacte dont dépend la conclusion.

Pénalisation (Étape 7) : la contrainte d'égalité est reportée dans le coût,

    J(q) = qᵀCq + µ‖Aq − b‖²

Le sujet interdit les multiplicateurs de Lagrange (Contrainte méthodologique 2).
J reste convexe comme somme de deux formes quadratiques convexes, car µ‖Aq − b‖²
est convexe pour tout µ ≥ 0 puisque AᵀA est semi-définie positive. Ce que le
rapport doit ajouter : la solution pénalisée ne satisfait Aq = b qu'à la limite
µ → ∞, et le résidu ‖Aq* − b‖ est donc une quantité à mesurer, pas à supposer
nulle.

Gradient (Étape 8, à dériver ligne par ligne dans le rapport) :

    ∇J(q) = 2Cq + 2µ Aᵀ(Aq − b)

Les deux facteurs 2 et la transposition de A sont les erreurs classiques
signalées en section 14 du plan. ``verifier_gradient`` ci-dessous existe pour
les attraper avant qu'elles ne contaminent toutes les expériences.
---------------------------------------------------------------------------
"""

from __future__ import annotations

import numpy as np


def cout(q: np.ndarray, couts: np.ndarray) -> float:
    """Coût technique brut Σ c_e q_e², sans terme de pénalisation.

    C'est la quantité qui a un sens pour la société de distribution, et donc la
    métrique de comparaison finale entre la stratégie de référence et q*. Le
    terme de pénalisation, lui, est un artefact de méthode : le faire figurer
    dans le tableau comparatif du rapport fausserait la comparaison, puisque la
    stratégie de référence n'est pas issue d'une pénalisation.

    Args:
        q: vecteur des débits, longueur |E|.
        couts: vecteur des c_e, longueur |E|.
    """
    raise NotImplementedError("M5 à partir de M4, Étape 7.")


def violation_contrainte(q: np.ndarray, A: np.ndarray, b: np.ndarray) -> float:
    """Norme du résidu de conservation, ‖Aq − b‖.

    Mesure à quel point la solution pénalisée respecte réellement la
    conservation des flux. C'est la métrique centrale de l'Expérience 3 :
    elle doit décroître quand µ augmente.
    """
    raise NotImplementedError("M5 à partir de M4, Étape 7.")


def objectif(q: np.ndarray, A: np.ndarray, b: np.ndarray, couts: np.ndarray, mu: float) -> float:
    """Fonction de coût pénalisée J(q) = qᵀCq + µ‖Aq − b‖².

    Args:
        q: débits, longueur |E|.
        A: matrice d'incidence, forme (|V|, |E|).
        b: second membre de conservation, longueur |V|.
        couts: vecteur des c_e, longueur |E|.
        mu: paramètre de pénalisation, strictement positif.

    Returns:
        La valeur de J en q.
    """
    raise NotImplementedError("M5 à partir de la dérivation validée de M4, Étape 7.")


def gradient(q: np.ndarray, A: np.ndarray, b: np.ndarray, couts: np.ndarray, mu: float) -> np.ndarray:
    """Gradient ∇J(q) = 2Cq + 2µ Aᵀ(Aq − b).

    À implémenter *littéralement* d'après la dérivation manuscrite de M4, sans
    réécriture algébrique intermédiaire : une simplification introduite au
    clavier casse la correspondance entre le rapport et le code, qui est
    précisément ce que la Contrainte méthodologique 1 demande de préserver.

    Note de performance, sans effet sur le résultat : calculer ``A.T @ (A @ q - b)``
    et non ``(A.T @ A) @ q - A.T @ b``. La première forme fait deux produits
    matrice-vecteur, la seconde construit une matrice |E|×|E| à chaque appel,
    des milliers de fois dans la boucle de descente.

    Returns:
        Le gradient en q, longueur |E|.
    """
    raise NotImplementedError(
        "M5 à partir de la dérivation validée et relue de M4, Étape 8. "
        "Vérifier ensuite avec verifier_gradient."
    )


def hessienne(A: np.ndarray, couts: np.ndarray, mu: float) -> np.ndarray:
    """Hessienne constante H = 2C + 2µ AᵀA.

    J étant quadratique, sa hessienne ne dépend pas de q : elle se calcule une
    fois et sert à la fois à établir la borne sur le pas (λ_max) et à discuter
    le conditionnement du problème pénalisé.
    """
    raise NotImplementedError("M5 à partir de M4, Étapes 8 et 9.")


def verifier_gradient(
    q: np.ndarray, A: np.ndarray, b: np.ndarray, couts: np.ndarray, mu: float, h: float = 1e-6
) -> float:
    """Confronte le gradient analytique aux différences finies centrées.

    Garde-fou contre les erreurs de dérivation les plus coûteuses : facteur 2
    oublié, Aᵀ écrit A, signe de b inversé. Ces trois-là ne font pas planter le
    code : elles produisent un q* faux, plausible, et invalident silencieusement
    toutes les expériences.

    Pour chaque composante e :

        ∂J/∂q_e ≈ [ J(q + h·e_e) − J(q − h·e_e) ] / (2h)

    La différence *centrée* et non décentrée : son erreur est en O(h²) au lieu
    de O(h), ce qui permet de distinguer une vraie erreur de dérivation du bruit
    d'arrondi.

    Cette vérification ne remplace pas la dérivation manuscrite exigée par le
    sujet, elle la contrôle. Un gradient qui passe ce test mais n'est pas
    dérivé dans le rapport reste une violation de la Contrainte
    méthodologique 1.

    Returns:
        L'écart relatif maximal entre gradient analytique et numérique. Un
        ordre de grandeur de 1e-6 ou moins indique une dérivation correcte.
    """
    raise NotImplementedError("M5, contrôle des Étapes 7 et 8, à écrire avant le solveur.")
