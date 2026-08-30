"""Analyse du graphe et de sa matrice : connexité, fragilité, rang, conditionnement.

Responsable : M2, en collaboration avec M1.
Dépend de : ``build_graph``.
Alimente : M4 (borne sur le pas d'apprentissage) et M6 (Expérience 5).
Étapes 2 et 3 du pipeline.

C'est ici que se joue la démonstration centrale du volet algèbre linéaire :
un réseau mal maillé se traduit *directement* par une instabilité numérique de
la résolution. Le graphe et le conditionnement ne sont pas deux sujets
distincts, c'est le même fait vu deux fois.
"""

from __future__ import annotations

import numpy as np

# Tolérance numérique en dessous de laquelle une valeur singulière ou une
# valeur propre est considérée comme nulle (bruit de calcul flottant), très
# en dessous de la plus petite valeur non nulle attendue (~0.5 sur le réseau
# de référence) pour ne jamais masquer une direction physique du noyau.
SEUIL_NUMERIQUE = 1e-9


def est_connexe(graphe) -> bool:
    """Teste la connexité du réseau.

    Le sujet demande de vérifier qu'aucun quartier n'est isolé. Attention à
    quelle connexité : sur un graphe orienté, la connexité *faible* (le graphe
    non orienté sous-jacent est connexe) suffit à garantir qu'aucun quartier
    n'est physiquement coupé du réseau. La connexité *forte* serait trop
    exigeante ici, puisque l'eau descend des réservoirs vers les quartiers et
    ne remonte pas : le rapport doit dire laquelle est retenue et pourquoi.

    Returns:
        True si le réseau est faiblement connexe.
    """
    import networkx as nx

    if graphe.is_directed():
        return nx.is_weakly_connected(graphe)
    return nx.is_connected(graphe)


def composantes_connexes(graphe) -> list[set[str]]:
    """Retourne les composantes connexes, pour localiser une éventuelle rupture.

    Si le réseau n'est pas connexe, le livrable n'est pas « échec » mais
    « zones non connexes identifiées et justifiées » (section 10.5 du plan).
    """
    import networkx as nx

    if graphe.is_directed():
        return [set(composante) for composante in nx.weakly_connected_components(graphe)]
    return [set(composante) for composante in nx.connected_components(graphe)]


def detecter_points_de_fragilite(graphe) -> dict[str, list]:
    """Identifie les fragilités structurelles du réseau.

    Trois notions distinctes, à ne pas confondre dans le rapport :

    - **nœuds de degré 1** : un quartier alimenté par une seule conduite. Sa
      coupure le prive totalement d'eau.
    - **arêtes pont (isthmes)** : une conduite dont le retrait déconnecte le
      graphe. Sa coupure peut priver *plusieurs* quartiers à la fois.
    - **points d'articulation** : un nœud dont le retrait déconnecte le graphe.

    Le réseau de référence contient volontairement un cas de chaque type autour
    de Q10 : c'est le cas de test naturel de cette fonction.

    Les trois notions sont définies sur le graphe *non orienté* sous-jacent :
    l'orientation des conduites est une convention de modélisation pour A
    (cf. build_graph.py), pas une contrainte physique sur la propagation
    d'une panne (hypothèses de M1). Si ``graphe`` est orienté, il est donc
    converti avant analyse.

    Returns:
        Un dictionnaire aux clés ``noeuds_degre_1``, ``aretes_pont`` et
        ``points_articulation``.
    """
    import networkx as nx

    non_oriente = graphe.to_undirected() if graphe.is_directed() else graphe

    noeuds_degre_1 = [noeud for noeud, degre in non_oriente.degree() if degre == 1]
    aretes_pont = list(nx.bridges(non_oriente))
    points_articulation = list(nx.articulation_points(non_oriente))

    return {
        "noeuds_degre_1": noeuds_degre_1,
        "aretes_pont": aretes_pont,
        "points_articulation": points_articulation,
    }


def rang(A: np.ndarray) -> int:
    """Calcule le rang de la matrice d'incidence.

    Résultat classique à démontrer dans le rapport, pas seulement à mesurer :
    pour un graphe orienté à ``n`` nœuds et ``k`` composantes connexes,

        rang(A) = n − k

    Autrement dit, sur un réseau connexe, A a un rang déficient de 1 : les
    lignes somment à zéro, car chaque arête apporte un +1 et un −1. La
    conséquence est concrète et doit être discutée : le système Aq = b n'a pas
    de solution unique, il en a tout un espace affine de dimension |E| − n + 1.
    C'est précisément ce qui justifie qu'on *choisisse* parmi ces solutions
    celle qui minimise Σ c_e q_e² : sans ce déficit de rang, il n'y aurait rien
    à optimiser.

    Note d'implémentation : ``numpy.linalg.matrix_rank`` décide du rang par un
    seuil sur les valeurs singulières. Sur une matrice mal conditionnée, ce
    seuil devient discutable. Le mentionner dans le rapport plutôt que de
    présenter le rang comme une valeur exacte.
    """
    return int(np.linalg.matrix_rank(A, tol=SEUIL_NUMERIQUE))


def noyau(A: np.ndarray) -> np.ndarray:
    """Retourne une base du noyau de A.

    Le noyau a une lecture physique directe : ses vecteurs sont les circulations
    de débit le long des cycles du réseau, qui ne changent rien au bilan de
    conservation à chaque nœud. Ajouter un élément du noyau à une solution
    admissible en redonne une autre, de coût différent. Ce sont exactement les
    degrés de liberté que l'optimisation exploite.

    Sa dimension vaut |E| − rang(A), soit le nombre cyclomatique du graphe :
    le lien entre structure discrète et algèbre est ici littéral.

    Implémentation : ``scipy.linalg.null_space`` calcule une base
    orthonormée du noyau par SVD, valable pour n'importe quelle matrice
    d'incidence (pas seulement celle du réseau de référence). Cette base
    n'est pas la base "cyclique" à coefficients ±1/0 utilisée pour
    l'illustration dans le rapport (une par cycle fondamental de l'arbre
    couvrant) : les deux bases engendrent le même sous-espace, mais la
    seconde est plus lisible pour l'interprétation physique, la première
    est plus robuste numériquement et généralise à tout graphe.

    Returns:
        Une base orthonormée du noyau, de forme (|E|, dim(ker A)). Un
        tableau de forme (|E|, 0) si le noyau est réduit à {0}.
    """
    from scipy.linalg import null_space

    return null_space(A, rcond=SEUIL_NUMERIQUE)


def conditionnement(A: np.ndarray) -> float:
    """Calcule le conditionnement pertinent pour la descente de gradient.

    Piège à éviter : sur un réseau connexe, A est de rang déficient, donc
    ``cond(A)`` est infini et ne dit rien d'utile. Ce qui gouverne réellement la
    vitesse de convergence, c'est le conditionnement de la hessienne du problème
    *pénalisé*,

        H = 2C + 2µ AᵀA

    qui, elle, est définie positive dès que c_e > 0, même quand AᵀA est
    singulière. C'est le terme Σ c_e q_e² qui régularise le problème. Le
    calcul exact de κ(H), qui dépend des coûts c_e et de µ, est fait par
    ``constante_de_lipschitz`` ci-dessous (qui retourne λ_max(H), la seule
    quantité utile à M4).

    La présente fonction retourne, elle, le conditionnement *effectif* de A
    seule (indépendant de c_e et µ), défini comme le rapport de la plus
    grande à la plus petite valeur singulière strictement positive de A. Ce
    conditionnement caractérise la structure du réseau seule, indépendamment
    de tout choix de coûts ou de pénalisation : c'est la quantité comparée
    entre variantes de maillage à l'Expérience 5, où l'on veut isoler l'effet
    du graphe sans le mélanger à un choix de µ.

    Le rapport doit expliciter ce glissement de κ(A) vers κ(H), et le fait que
    κ(H) dépend de µ : augmenter µ resserre la contrainte mais dégrade le
    conditionnement, donc ralentit la convergence. C'est exactement le compromis
    que mesure l'Expérience 3.

    Args:
        A: la matrice d'incidence.

    Returns:
        Le conditionnement effectif κ(A) = σ_max(A) / σ_min⁺(A), calculé sur
        les seules valeurs singulières strictement positives.
    """
    valeurs_singulieres = np.linalg.svd(A, compute_uv=False)
    sv_positives = valeurs_singulieres[valeurs_singulieres > SEUIL_NUMERIQUE]
    if sv_positives.size == 0:
        raise ValueError("A est la matrice nulle : aucune valeur singulière strictement positive.")
    return float(sv_positives.max() / sv_positives.min())


def constante_de_lipschitz(A: np.ndarray, couts: np.ndarray, mu: float) -> float:
    """Calcule L, la constante de Lipschitz du gradient de J.

    J étant quadratique, ∇J est linéaire et L est simplement la plus grande
    valeur propre de la hessienne constante

        H = 2C + 2µ AᵀA        avec  C = diag(c_e)

    H est symétrique : utiliser ``numpy.linalg.eigvalsh`` et non ``eigvals``,
    qui renverrait des valeurs propres complexes à partie imaginaire numérique
    et rendrait la comparaison au seuil 2/L bancale.

    C'est cette valeur qui donne la borne de convergence η < 2/L établie par
    M4 et testée par l'Expérience 4. Sans elle, le choix du pas est arbitraire,
    et l'analyse de convergence perd toute crédibilité (section 14 du plan).

    Args:
        A: matrice d'incidence.
        couts: vecteur des c_e.
        mu: paramètre de pénalisation.

    Returns:
        L = λ_max(2C + 2µAᵀA).
    """
    C = np.diag(np.asarray(couts, dtype=float))
    H = 2.0 * C + 2.0 * mu * (A.T @ A)
    return float(np.linalg.eigvalsh(H).max())


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # generate_network.py vit dans data/, build_graph.py dans le même
    # dossier que ce script : on ajoute les deux au chemin de recherche.
    racine_projet = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(racine_projet / "data"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from build_graph import construire_graphe, construire_matrice_incidence, vecteur_couts
    from data.generate_network import charger_reseau

    chemin_config = racine_projet / "data" / "network_config.json"
    reseau = charger_reseau(chemin_config)

    graphe = construire_graphe(reseau)
    A = construire_matrice_incidence(reseau)
    couts = vecteur_couts(reseau)

    print("=== CONNEXITÉ ET FRAGILITÉ ===")
    print(f"Connexe (faiblement) : {est_connexe(graphe)}")
    print(f"Composantes connexes : {composantes_connexes(graphe)}")
    fragilites = detecter_points_de_fragilite(graphe)
    print(f"Nœuds de degré 1     : {fragilites['noeuds_degre_1']}")
    print(f"Arêtes-ponts         : {fragilites['aretes_pont']}")
    print(f"Points d'articulation: {fragilites['points_articulation']}")

    print("\n=== ALGÈBRE LINÉAIRE ===")
    r = rang(A)
    K = noyau(A)
    print(f"rang(A) = {r}  (attendu n - k = {len(reseau.noeuds)} - 1 = {len(reseau.noeuds) - 1})")
    print(f"dim(ker A) = {K.shape[1]}  (base orthonormée de forme {K.shape})")
    print(f"kappa(A) effectif = {conditionnement(A):.4f}")

    mu_exemple = 1.0
    L = constante_de_lipschitz(A, couts, mu_exemple)
    print(f"L = lambda_max(2C + 2*mu*A^T A) pour mu={mu_exemple} : {L:.4f}")
    print(f"  -> pas d'apprentissage recommandé eta < 2/L = {2 / L:.6f}")