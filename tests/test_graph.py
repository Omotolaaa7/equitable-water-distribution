"""Garde-fous sur le graphe et la matrice d'incidence — périmètre M2."""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Bloqué par l'Étape 3 — construction de A par M2.")
def test_colonnes_de_A_somment_a_zero():
    """Chaque colonne de A porte exactement un +1 et un −1.

    Conséquence directe de la définition de la matrice d'incidence orientée :
    une arête sort d'un nœud et entre dans un autre. Ce test attrape une erreur
    de convention de signe, qui ne fait rien planter mais inverse le sens
    physique de Aq = b.
    """


@pytest.mark.skip(reason="Bloqué par l'Étape 3.")
def test_rang_egale_n_moins_composantes():
    """rang(A) = n − k, où k est le nombre de composantes connexes.

    Confronte la mesure numérique au résultat démontré dans le rapport. Sur le
    réseau de référence, connexe, on attend rang(A) = |V| − 1.
    """


@pytest.mark.skip(reason="Bloqué par l'Étape 2.")
def test_q10_detecte_comme_point_de_fragilite():
    """Q10 n'est relié que par la conduite Q9 → Q10.

    Cette fragilité est délibérément placée dans le réseau de référence : c'est
    le cas de test naturel de ``detecter_points_de_fragilite``.
    """
