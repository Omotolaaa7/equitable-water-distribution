"""Contrôle de la dérivation du gradient, périmètre M5, d'après M4.

Les formules testées ici viennent de `docs/section_optimisation_membre4.pdf`,
rédigé par Aïchatou Traoré. Le code de `src/optimization/` en est la traduction
littérale, et ces tests vérifient que la traduction est fidèle.

Le premier test est le plus précieux du fichier : il reprend l'exemple à deux
conduites que le Membre 4 a calculé à la main dans son document, avec ses
valeurs numériques. Si le code y répond juste, c'est que la chaîne allant de la
dérivation manuscrite au code tient.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.optimization.objective import (
    cout,
    gradient,
    hessienne,
    objectif,
    verifier_gradient,
    violation_contrainte,
)


@pytest.fixture
def exemple_membre_4():
    """Le réseau à deux conduites de la section 1.3 du document du Membre 4.

    Un réservoir R1 alimente Q1, qui demande 4, et Q2, qui demande 6, par deux
    conduites directes de coût unitaire 1. Le Membre 4 évalue tout en q = (3, 5)
    avec µ = 10, et publie les résultats que ce fichier vérifie.
    """
    A = np.array([[-1.0, -1.0], [1.0, 0.0], [0.0, 1.0]])
    b = np.array([-10.0, 4.0, 6.0])
    couts = np.array([1.0, 1.0])
    q = np.array([3.0, 5.0])
    return A, b, couts, q, 10.0


def test_exemple_calcule_a_la_main_par_le_membre_4(exemple_membre_4):
    """Reproduit les quatre valeurs publiées dans le document du Membre 4."""
    A, b, couts, q, mu = exemple_membre_4

    assert cout(q, couts) == pytest.approx(34.0)
    assert (A @ q - b) == pytest.approx(np.array([2.0, -1.0, -1.0]))
    assert objectif(q, A, b, couts, mu) == pytest.approx(94.0)
    assert gradient(q, A, b, couts, mu) == pytest.approx(np.array([-54.0, -50.0]))


def test_gradient_analytique_contre_differences_finies(exemple_membre_4):
    """L'écart relatif entre ∇J analytique et numérique reste sous 1e-6.

    Attrape les trois erreurs listées en section 14 du plan : facteur 2 oublié,
    mauvaise transposition de A, signe de b inversé. Aucune des trois ne fait
    planter le code, elles produisent un q* faux et plausible, et invalident
    silencieusement les six expériences.
    """
    A, b, couts, _, mu = exemple_membre_4
    generateur = np.random.default_rng(0)

    for _ in range(10):
        q = generateur.uniform(0.0, 20.0, size=A.shape[1])
        assert verifier_gradient(q, A, b, couts, mu) < 1e-6


def test_gradient_faux_serait_detecte(exemple_membre_4):
    """Le contrôle par différences finies doit vraiment avoir des dents.

    On simule deux des erreurs les plus courantes, l'oubli du facteur 2 et le
    signe de b inversé, et on vérifie que le résultat diffère du gradient juste. Sans ce
    test, rien ne garantit que `verifier_gradient` sait détecter quoi que ce soit.
    """
    A, b, couts, q, mu = exemple_membre_4
    juste = gradient(q, A, b, couts, mu)

    sans_le_facteur_deux = couts * q + mu * (A.T @ (A @ q - b))
    signe_de_b_inverse = 2.0 * couts * q + 2.0 * mu * (A.T @ (A @ q + b))

    assert not np.allclose(juste, sans_le_facteur_deux)
    assert not np.allclose(juste, signe_de_b_inverse)


def test_hessienne_coherente_avec_le_gradient(exemple_membre_4):
    """∇J étant linéaire, ∇J(q₁) − ∇J(q₂) doit valoir exactement H(q₁ − q₂).

    C'est la vérification de cohérence que le Membre 4 signale en section 3.4 :
    re-dériver le gradient doit redonner le Hessien établi en section 2.4.
    """
    A, b, couts, _, mu = exemple_membre_4
    H = hessienne(A, couts, mu)
    generateur = np.random.default_rng(1)

    q1 = generateur.uniform(0.0, 20.0, size=A.shape[1])
    q2 = generateur.uniform(0.0, 20.0, size=A.shape[1])

    ecart_gradients = gradient(q1, A, b, couts, mu) - gradient(q2, A, b, couts, mu)
    assert ecart_gradients == pytest.approx(H @ (q1 - q2))


def test_hessienne_est_definie_positive(exemple_membre_4):
    """Toutes les valeurs propres de 2C + 2µAᵀA sont strictement positives.

    Contrepartie numérique de la démonstration de convexité du Membre 4, section
    2.4. Son résultat clé est que la conclusion ne dépend que de la stricte
    positivité des coûts, donc elle doit tenir pour tout µ, y compris nul.
    """
    A, _, couts, _, _ = exemple_membre_4

    for mu in (0.0, 1.0, 100.0, 10_000.0):
        assert np.all(np.linalg.eigvalsh(hessienne(A, couts, mu)) > 0)


def test_cout_nul_casserait_la_convexite(exemple_membre_4):
    """Si un coût unitaire tombe à zéro, la stricte convexité tombe avec lui.

    Ce test ne vérifie pas le code, il vérifie que l'hypothèse du Membre 4 est
    bien celle qu'il annonce. C'est aussi la raison pour laquelle
    `valider_reseau` refuse un coût nul.
    """
    A, _, _, _, _ = exemple_membre_4
    couts_degeneres = np.array([1.0, 0.0])

    valeurs_propres = np.linalg.eigvalsh(hessienne(A, couts_degeneres, mu=0.0))
    assert np.min(valeurs_propres) == pytest.approx(0.0)


def test_violation_est_nulle_sur_une_solution_admissible(exemple_membre_4):
    """Un q qui respecte exactement Aq = b doit donner une violation nulle."""
    A, b, _, _, _ = exemple_membre_4
    q_admissible = np.array([4.0, 6.0])

    assert A @ q_admissible == pytest.approx(b)
    assert violation_contrainte(q_admissible, A, b) == pytest.approx(0.0)
