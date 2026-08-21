"""Construction du graphe G = (V, E) et de sa matrice d'incidence A.

Responsable : M2, en collaboration avec M1.
Dépend de : la topologie figée par M1 (``data/generate_network.py``).
Alimente : M4 (qui a besoin de A pour la borne sur le pas) et toute
l'optimisation.
Étapes 2 et 3 du pipeline.

La matrice d'incidence est le pivot du projet : c'est elle qui fait passer de
la structure discrète (qui est relié à qui) à l'algèbre linéaire (le système
de conservation des flux), et c'est le système de conservation qui donne le
terme pénalisé µ‖Aq − b‖² dont M4 dérive le gradient.
"""

from __future__ import annotations

import numpy as np

# NOTE : import différé de networkx tant que le module n'est pas implémenté,
# pour que le dépôt reste importable avant l'installation des dépendances.


def construire_graphe(reseau):
    """Construit le graphe orienté networkx correspondant au réseau.

    Chaque nœud porte son type (``reservoir`` ou ``quartier``) et, pour les
    quartiers, ses paramètres de demande µ_i et σ_i. Chaque arête porte sa
    capacité et son coût unitaire c_e.

    Args:
        reseau: le ``Reseau`` livré par M1.

    Returns:
        Un ``networkx.DiGraph``.
    """
    raise NotImplementedError("M2 — Étape 2.")


def construire_matrice_incidence(reseau) -> np.ndarray:
    """Construit la matrice d'incidence orientée A du réseau.

    Convention à fixer et à écrire noir sur blanc dans le rapport, car deux
    conventions opposées coexistent dans la littérature. Celle retenue ici :

        A[i, e] = +1  si l'arête e *entre* dans le nœud i
        A[i, e] = -1  si l'arête e *sort* du nœud i
        A[i, e] =  0  sinon

    Avec cette convention, la ligne i de Aq = b s'écrit

        (flux entrant en i) − (flux sortant de i) = b_i

    c'est-à-dire la conservation des flux au nœud i, avec b_i = +D_i la demande
    consommée au quartier i, et b_i = −offre_i l'eau injectée au réservoir i.
    Le signe de b n'est pas anodin : l'inverser change la solution sans lever
    la moindre erreur. M1 doit valider l'interprétation physique, M2 le codage.

    Forme : ``(|V|, |E|)`` — une ligne par nœud, une colonne par conduite.

    Args:
        reseau: le ``Reseau`` livré par M1.

    Returns:
        A, de forme (|V|, |E|), dans l'ordre de nœuds donné par ``reseau.noeuds``.
    """
    raise NotImplementedError(
        "M2 — Étape 3. Livrable : A codée et testée, plus l'interprétation "
        "physique de Aq = b rédigée et validée (checklist, section 13)."
    )


def construire_second_membre(reseau, demandes: np.ndarray) -> np.ndarray:
    """Construit le vecteur b de conservation pour un scénario de demande donné.

    b dépend du scénario, pas seulement du réseau : c'est le point où
    l'incertitude probabiliste entre dans le problème d'optimisation. Un tirage
    Monte-Carlo de M5 produit un vecteur ``demandes``, qui produit un b, qui
    produit un q* différent.

    Args:
        reseau: le ``Reseau``.
        demandes: vecteur des D_i, dans l'ordre de ``reseau.quartiers``.

    Returns:
        b, de longueur |V|, aligné sur ``reseau.noeuds``.
    """
    raise NotImplementedError("M2 — Étape 3, avec M3 pour le format des demandes.")


def vecteur_couts(reseau) -> np.ndarray:
    """Retourne le vecteur des coûts unitaires (c_e), dans l'ordre des arêtes.

    C'est la diagonale de la matrice C = diag(c_e) qui apparaît dans
    ∇J(q) = 2Cq + 2µAᵀ(Aq − b). Sa stricte positivité est la condition de
    convexité de J : elle est vérifiée par ``valider_reseau``, et doit être
    citée comme hypothèse dans la démonstration de M4.
    """
    raise NotImplementedError("M2 — Étape 3.")
