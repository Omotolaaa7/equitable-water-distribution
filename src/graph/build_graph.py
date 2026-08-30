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

# Import différé de networkx : uniquement à l'intérieur de construire_graphe,
# pour que le reste du module (matrice A, second membre, coûts) reste
# importable et testable même sans networkx installé.


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
    import networkx as nx

    graphe = nx.DiGraph()

    for r in reseau.reservoirs:
        graphe.add_node(r.identifiant, type="reservoir", offre=r.offre)

    for q in reseau.quartiers:
        graphe.add_node(q.identifiant, type="quartier", mu=q.mu, sigma=q.sigma)

    for c in reseau.conduites:
        graphe.add_edge(c.source, c.cible, capacite=c.capacite, cout=c.cout)

    return graphe

def afficher_graphe(graphe):
    """Affiche graphiquement le graphe orienté avec NetworkX et Matplotlib."""

    import matplotlib.pyplot as plt
    import networkx as nx

    # Position des nœuds
    pos = nx.spring_layout(graphe, seed=42)

    # Création de la figure
    plt.figure(figsize=(10, 7))

    # Dessin du graphe
    nx.draw_networkx(
        graphe,
        pos,
        with_labels=True,
        arrows=True,
        node_size=2000,
        font_size=10,
        arrowsize=20
    )

    # Affichage des capacités et coûts sur les arcs
    labels = {
        (source, cible): f"cap={data['capacite']}, c={data['cout']}"
        for source, cible, data in graphe.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        graphe,
        pos,
        edge_labels=labels,
        font_size=8
    )

    plt.title("Graphe orienté du réseau de distribution d'eau")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

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

    Forme : ``(|V|, |E|)``, une ligne par nœud, une colonne par conduite.

    Args:
        reseau: le ``Reseau`` livré par M1.

    Returns:
        A, de forme (|V|, |E|), dans l'ordre de nœuds donné par ``reseau.noeuds``.
    """
    noeuds = reseau.noeuds
    index_noeud = {identifiant: i for i, identifiant in enumerate(noeuds)}

    n = len(noeuds)
    m = len(reseau.conduites)
    A = np.zeros((n, m), dtype=float)

    for e, conduite in enumerate(reseau.conduites):
        A[index_noeud[conduite.cible], e] = +1.0   # l'arête entre dans cible
        A[index_noeud[conduite.source], e] = -1.0  # l'arête sort de source

    return A


def construire_second_membre(reseau, demandes: np.ndarray) -> np.ndarray:
    """Construit le vecteur b de conservation pour un scénario de demande donné.

    b dépend du scénario, pas seulement du réseau : c'est le point où
    l'incertitude probabiliste entre dans le problème d'optimisation. Un tirage
    Monte-Carlo de M5 produit un vecteur ``demandes``, qui produit un b, qui
    produit un q* différent.

    Hypothèse à valider avec M1/M4 : la part de la demande totale injectée par
    chaque réservoir n'est pas spécifiée par le sujet. On la répartit ici au
    prorata de l'offre maximale de chaque réservoir (offre_i / Σ offre), ce qui
    garantit la conservation globale (Σ b = 0) quel que soit le scénario tiré,
    tant que la demande totale ne dépasse pas l'offre totale. Si le groupe
    préfère une autre règle de répartition (ex. décidée par M4 comme variable
    libre du problème d'optimisation), cette fonction est le seul endroit à
    modifier.

    Args:
        reseau: le ``Reseau``.
        demandes: vecteur des D_i, dans l'ordre de ``reseau.quartiers``.

    Returns:
        b, de longueur |V|, aligné sur ``reseau.noeuds``.
    """
    noeuds = reseau.noeuds
    index_noeud = {identifiant: i for i, identifiant in enumerate(noeuds)}
    n = len(noeuds)

    demandes = np.asarray(demandes, dtype=float)
    if demandes.shape != (len(reseau.quartiers),):
        raise ValueError(
            f"demandes doit être de longueur {len(reseau.quartiers)} "
            f"(un débit par quartier, dans l'ordre de reseau.quartiers), "
            f"reçu de forme {demandes.shape}."
        )

    b = np.zeros(n, dtype=float)

    # Quartiers : b_i = +D_i (demande consommée).
    for quartier, d_i in zip(reseau.quartiers, demandes):
        b[index_noeud[quartier.identifiant]] = d_i

    # Réservoirs : b_i = -offre_i injectée, répartie au prorata des offres
    # maximales déclarées par M1 (voir hypothèse documentée ci-dessus).
    offre_totale = sum(r.offre for r in reseau.reservoirs)
    demande_totale = float(demandes.sum())
    for r in reseau.reservoirs:
        part = r.offre / offre_totale
        b[index_noeud[r.identifiant]] = -part * demande_totale

    return b


def vecteur_couts(reseau) -> np.ndarray:
    """Retourne le vecteur des coûts unitaires (c_e), dans l'ordre des arêtes.

    C'est la diagonale de la matrice C = diag(c_e) qui apparaît dans
    ∇J(q) = 2Cq + 2µAᵀ(Aq − b). Sa stricte positivité est la condition de
    convexité de J : elle est vérifiée par ``valider_reseau``, et doit être
    citée comme hypothèse dans la démonstration de M4.
    """
    return np.array([c.cout for c in reseau.conduites], dtype=float)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # generate_network.py vit dans data/, un dossier frère de src/ : on
    # l'ajoute explicitement au chemin de recherche des modules.
    racine_projet = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(racine_projet / "data"))

    from data.generate_network import charger_reseau

    chemin_config = racine_projet / "data" / "network_config.json"
    reseau = charger_reseau(chemin_config)

    graphe = construire_graphe(reseau)
    A = construire_matrice_incidence(reseau)
    afficher_graphe(graphe)
    
    c = vecteur_couts(reseau)
    b_exemple = construire_second_membre(
        reseau, demandes=np.array([q.mu for q in reseau.quartiers])
    )

    print("=== CONSTRUCTION DU GRAPHE ET DE LA MATRICE D'INCIDENCE ===")
    print(f"Graphe : {graphe.number_of_nodes()} nœuds, {graphe.number_of_edges()} arêtes")
    print(f"Matrice A : forme {A.shape}")
    print("\nMatrice d'incidence A :")
    print(A)
    print(f"Vecteur des coûts c_e : {c}")
    print(f"Second membre b (demandes = µ) : {b_exemple}, somme = {b_exemple.sum():.6f}")