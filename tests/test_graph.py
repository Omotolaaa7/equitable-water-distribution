"""Garde-fous sur le graphe et la matrice d'incidence, périmètre M2.

Le solveur du Membre 5 repose entièrement sur la matrice `A` produite ici. Une
erreur de convention ou de signe ne ferait rien planter, elle donnerait un `q*`
faux et plausible. Ces tests protègent donc autant le travail de M2 que celui
qui vient après.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from data.generate_network import charger_reseau
from src.graph.build_graph import (
    construire_graphe,
    construire_matrice_incidence,
    construire_second_membre,
    vecteur_couts,
)
from src.graph import graph_analysis as ga

CONFIG = Path(__file__).resolve().parents[1] / "data" / "network_config.json"


@pytest.fixture(scope="module")
def reseau():
    return charger_reseau(CONFIG)


@pytest.fixture(scope="module")
def matrice(reseau):
    return construire_matrice_incidence(reseau)


def test_colonnes_de_A_somment_a_zero(matrice):
    """Chaque colonne de A porte exactement un +1 et un −1.

    Conséquence directe de la définition de la matrice d'incidence orientée :
    une conduite sort d'un nœud et entre dans un autre. Ce test attrape une
    erreur de convention de signe, qui ne fait rien planter mais inverse le sens
    physique de Aq = b.
    """
    assert np.allclose(matrice.sum(axis=0), 0.0)

    for colonne in matrice.T:
        assert np.count_nonzero(colonne == 1.0) == 1
        assert np.count_nonzero(colonne == -1.0) == 1
        assert np.count_nonzero(colonne) == 2


def test_rang_egale_n_moins_composantes(reseau, matrice):
    """rang(A) = n − k, où k est le nombre de composantes connexes.

    Confronte la mesure numérique au résultat démontré dans le rapport. Sur le
    réseau de référence, connexe, on attend rang(A) = |V| − 1, soit 9.
    """
    graphe = construire_graphe(reseau)
    assert ga.est_connexe(graphe)

    n = len(reseau.noeuds)
    k = len(ga.composantes_connexes(graphe))

    assert ga.rang(matrice) == n - k
    assert ga.rang(matrice) == 9


def test_dimension_du_noyau_egale_le_nombre_de_boucles(reseau, matrice):
    """dim(ker A) = |E| − rang(A), soit le nombre cyclomatique du graphe."""
    attendue = len(reseau.conduites) - ga.rang(matrice)

    assert ga.noyau(matrice).shape[1] == attendue
    assert attendue == 4


def test_une_circulation_en_boucle_ne_change_rien(reseau, matrice):
    """Envoyer de l'eau en rond dans un cycle laisse le bilan de chaque nœud intact.

    C'est le résultat central du projet, vérifié sur une boucle explicite :
    Q2 vers Q3 puis Q3 vers Q4, contre le raccourci Q2 vers Q4.
    """
    identifiants = [f"{c.source}-{c.cible}" for c in reseau.conduites]
    circulation = np.zeros(len(identifiants))
    circulation[identifiants.index("Q2-Q3")] = 1.0
    circulation[identifiants.index("Q3-Q4")] = 1.0
    circulation[identifiants.index("Q2-Q4")] = -1.0

    assert matrice @ circulation == pytest.approx(np.zeros(matrice.shape[0]))


def test_q1_detecte_comme_point_de_fragilite(reseau):
    """Q1 n'est relié au réseau que par la conduite R1 vers Q1.

    Cette fragilité est délibérément placée dans le réseau de référence par le
    Membre 1, qui la documente dans ses hypothèses.

    Le test vérifie aussi que Q1 n'est pas un point d'articulation : le retirer
    ne coupe rien, puisque rien ne transite par lui. Confondre les deux notions
    est l'erreur classique de cette partie du rapport.
    """
    fragilites = ga.detecter_points_de_fragilite(construire_graphe(reseau))

    assert fragilites["noeuds_degre_1"] == ["Q1"]
    assert {"R1", "Q1"} in [set(pont) for pont in fragilites["aretes_pont"]]
    assert "Q1" not in fragilites["points_articulation"]


def test_second_membre_conserve_la_masse(reseau, matrice):
    """La somme de b doit valoir zéro : rien ne se crée ni ne se perd.

    Les réservoirs injectent en négatif ce que les quartiers consomment en
    positif. C'est le contrôle le plus simple de la construction de b, et il
    tient pour n'importe quel scénario de demande, pas seulement la moyenne.
    """
    generateur = np.random.default_rng(0)

    for _ in range(5):
        demandes = generateur.uniform(10.0, 80.0, size=len(reseau.quartiers))
        b = construire_second_membre(reseau, demandes)

        assert b.sum() == pytest.approx(0.0)
        assert b[len(reseau.reservoirs):] == pytest.approx(demandes)
        assert np.all(b[: len(reseau.reservoirs)] <= 0.0)


def test_conditionnement_est_fini_et_positif(matrice):
    """κ doit être exploitable, pas infini.

    Sur un réseau connexe avec des cycles, A est de rang déficient et la formule
    usuelle renverrait l'infini. Le Membre 2 calcule le rapport des valeurs
    singulières non nulles, qui reste fini.
    """
    valeur = ga.conditionnement(matrice)

    assert np.isfinite(valeur)
    assert valeur > 1.0
    assert valeur == pytest.approx(4.724, abs=1e-3)


def test_constante_de_lipschitz_croit_avec_mu(reseau, matrice):
    """L(µ) croît avec µ, ce qui réduit d'autant le pas maximal admissible.

    C'est le compromis établi en section 6.3 du document du Membre 4, vérifié
    ici sur le réseau réel. Pour µ = 1, il annonce L ≈ 14,95.
    """
    couts = vecteur_couts(reseau)
    valeurs = [ga.constante_de_lipschitz(matrice, couts, mu) for mu in (1.0, 10.0, 100.0)]

    assert valeurs == sorted(valeurs)
    assert valeurs[0] == pytest.approx(14.95, abs=0.05)


def test_tous_les_couts_sont_strictement_positifs(reseau):
    """L'hypothèse exacte dont dépend la convexité de J, section 2.4 du Membre 4."""
    assert np.all(vecteur_couts(reseau) > 0.0)
