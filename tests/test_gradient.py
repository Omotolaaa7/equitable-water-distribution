"""Contrôle de la dérivation du gradient, périmètre M5, d'après M4.

Bloqué par le jalon section 16. Ce fichier existe pour rappeler que la
première chose à faire après avoir codé ``gradient`` est de le confronter aux
différences finies, avant de lancer la moindre expérience.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Bloqué par le jalon section 16.")
def test_gradient_analytique_contre_differences_finies():
    """L'écart relatif entre ∇J analytique et numérique reste sous 1e-6.

    Attrape les trois erreurs listées en section 14 du plan : facteur 2 oublié,
    mauvaise transposition de A, signe de b inversé. Aucune des trois ne fait
    planter le code : elles produisent un q* faux et plausible, et invalident
    silencieusement les six expériences.
    """


@pytest.mark.skip(reason="Bloqué par le jalon section 16.")
def test_hessienne_est_definie_positive():
    """Toutes les valeurs propres de 2C + 2µAᵀA sont strictement positives.

    Contrepartie numérique de la démonstration de convexité de M4. Si ce test
    échoue alors que la démonstration tient, l'erreur est dans le code ; s'il
    échoue et que c_e n'est pas strictement positif, c'est le réseau qui est en
    faute, et ``valider_reseau`` aurait dû l'attraper plus tôt.
    """


@pytest.mark.skip(reason="Bloqué par le jalon section 16.")
def test_solution_du_cas_a_deux_conduites():
    """Sur deux conduites parallèles, le débit se répartit à l'inverse des coûts.

    Le petit cas vérifiable à la main exigé par la section 10.5 du plan.
    """
