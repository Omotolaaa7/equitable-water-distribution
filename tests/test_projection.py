"""Garde-fous sur la projection et la descente, périmètre M5.

L'algorithme testé ici est celui de la section 4.3 du document du Membre 4,
`docs/section_optimisation_membre4.pdf`.

Le test central est `test_deux_conduites_paralleles` : il vérifie le solveur sur
un cas dont la solution se pose à la main en trois lignes. La section 10.5 du
plan de projet en fait un critère de fin de livrable.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.optimization.gradient_descent import (
    descente_projetee,
    pas_maximal_theorique,
    projeter_orthant_positif,
)
from src.optimization.objective import cout, hessienne, violation_contrainte


@pytest.fixture
def deux_conduites_paralleles():
    """Un réservoir alimente un quartier par deux conduites, de coûts 1 et 3.

    La conservation impose q₁ + q₂ = 100. En remplaçant q₂ par 100 − q₁ dans
    c₁q₁² + c₂q₂² et en dérivant, l'optimum vérifie c₁q₁ = c₂q₂, donc les débits
    se répartissent en proportion inverse des coûts : q₁ = 75 et q₂ = 25.
    """
    A = np.array([[-1.0, -1.0], [1.0, 1.0]])
    b = np.array([-100.0, 100.0])
    couts = np.array([1.0, 3.0])
    return A, b, couts


def test_projection_ne_renvoie_jamais_de_negatif():
    """P(q) ≥ 0 pour tout q, y compris massivement négatif."""
    generateur = np.random.default_rng(0)
    q = generateur.uniform(-1e6, 1e6, size=50)

    assert np.all(projeter_orthant_positif(q) >= 0.0)


def test_projection_est_idempotente():
    """P(P(q)) = P(q).

    Propriété caractéristique d'une projection. Sa violation signalerait que la
    fonction fait autre chose : une remise à l'échelle, par exemple.
    """
    generateur = np.random.default_rng(1)
    q = generateur.uniform(-100.0, 100.0, size=30)

    une_fois = projeter_orthant_positif(q)
    assert projeter_orthant_positif(une_fois) == pytest.approx(une_fois)


def test_projection_laisse_intactes_les_composantes_positives():
    """Seules les composantes négatives bougent, les autres ne sont pas touchées."""
    q = np.array([-3.0, 0.0, 2.5, -0.1, 17.0])

    assert projeter_orthant_positif(q) == pytest.approx(np.array([0.0, 0.0, 2.5, 0.0, 17.0]))


def test_projection_donne_bien_le_point_admissible_le_plus_proche():
    """Contrôle direct de la proposition 2 du Membre 4, par force brute.

    On compare la projection à un balayage fin de l'orthant positif sur une
    seule composante. Ça ne remplace pas sa démonstration, ça la corrobore.
    """
    for x in (-5.0, -0.2, 0.0, 0.3, 12.0):
        candidats = np.linspace(0.0, 20.0, 200_001)
        meilleur = candidats[np.argmin((candidats - x) ** 2)]
        assert projeter_orthant_positif(np.array([x]))[0] == pytest.approx(meilleur, abs=1e-4)


def test_pas_maximal_vaut_bien_deux_sur_lambda_max(deux_conduites_paralleles):
    """La borne retournée doit être exactement 2/λmax(2C + 2µAᵀA), section 5.1."""
    A, _, couts = deux_conduites_paralleles

    for mu in (1.0, 10.0, 1000.0):
        L = np.linalg.eigvalsh(hessienne(A, couts, mu)).max()
        assert pas_maximal_theorique(A, couts, mu) == pytest.approx(2.0 / L)


def test_deux_conduites_paralleles(deux_conduites_paralleles):
    """Le petit cas dont la solution se pose à la main.

    On vérifie la condition d'optimalité c₁q₁ = c₂q₂ plutôt que les valeurs 75
    et 25 elles-mêmes : avec un µ fini, la pénalisation laisse volontairement un
    résidu sur la conservation, donc la somme des débits n'atteint pas
    exactement 100. C'est le comportement décrit en section 6.2 du Membre 4.
    """
    A, b, couts = deux_conduites_paralleles
    q, historique = descente_projetee(A, b, couts, mu=1000.0, tolerance=1e-12,
                                      max_iterations=200_000)

    assert historique.a_converge
    assert np.all(q >= 0.0)
    assert couts[0] * q[0] == pytest.approx(couts[1] * q[1], rel=1e-6)
    assert q[0] == pytest.approx(75.0, rel=1e-3)
    assert q[1] == pytest.approx(25.0, rel=1e-3)


def test_la_violation_decroit_quand_mu_augmente(deux_conduites_paralleles):
    """Section 6.2 du Membre 4 : ‖Aq* − b‖ tend vers 0 quand µ grandit."""
    A, b, couts = deux_conduites_paralleles
    violations = []

    for mu in (1.0, 10.0, 100.0, 1000.0):
        q, _ = descente_projetee(A, b, couts, mu=mu, tolerance=1e-12,
                                 max_iterations=200_000)
        violations.append(violation_contrainte(q, A, b))

    assert violations == sorted(violations, reverse=True)


def test_le_pas_maximal_decroit_comme_un_sur_mu(deux_conduites_paralleles):
    """Section 6.3 du Membre 4 : ηmax(µ) se comporte en 1/µ pour µ grand.

    Multiplier µ par 10 doit diviser le pas maximal par 10, à quelques pour cent
    près une fois le régime asymptotique atteint.
    """
    A, _, couts = deux_conduites_paralleles

    pas_cent = pas_maximal_theorique(A, couts, 100.0)
    pas_mille = pas_maximal_theorique(A, couts, 1000.0)

    assert pas_cent / pas_mille == pytest.approx(10.0, rel=0.02)


def test_un_pas_trop_grand_fait_diverger(deux_conduites_paralleles):
    """Section 5.2 : au-delà de la borne 2/L, la théorie ne garantit plus rien.

    C'est le protocole de l'Expérience 4, réduit à son plus simple appareil.

    Observation à reporter dans le rapport : avec la projection, dépasser la
    borne ne fait pas exploser les valeurs vers l'infini, comme ce serait le cas
    sans contrainte. Le `max(·, 0)` rabat les composantes négatives à chaque
    tour, ce qui borne la suite. On obtient une oscillation entretenue entre
    deux états, jamais un dépassement numérique. La conclusion pratique est la
    même, l'algorithme ne converge pas.
    """
    A, b, couts = deux_conduites_paralleles
    borne = pas_maximal_theorique(A, couts, mu=100.0)

    _, sous_la_borne = descente_projetee(A, b, couts, mu=100.0, eta=0.5 * borne,
                                         max_iterations=50_000)
    _, au_dessus = descente_projetee(A, b, couts, mu=100.0, eta=1.5 * borne,
                                     max_iterations=50_000)

    assert sous_la_borne.a_converge
    assert not au_dessus.a_converge

    # Sous la borne, J décroît. Au-dessus, il oscille : on le voit au fait que la
    # suite des valeurs remonte au moins une fois de façon franche.
    valeurs = np.array(au_dessus.valeurs_objectif)
    assert np.max(np.diff(valeurs)) > 1.0


def test_la_descente_fait_decroitre_le_cout(deux_conduites_paralleles):
    """Sous la borne, J(q_k) doit décroître à chaque itération."""
    A, b, couts = deux_conduites_paralleles
    _, historique = descente_projetee(A, b, couts, mu=100.0, max_iterations=500)

    valeurs = np.array(historique.valeurs_objectif)
    assert np.all(np.diff(valeurs) <= 1e-9)


def test_critere_inconnu_leve(deux_conduites_paralleles):
    """Une faute de frappe sur le critère doit lever, pas être ignorée."""
    A, b, couts = deux_conduites_paralleles

    with pytest.raises(ValueError, match="Critère d'arrêt inconnu"):
        descente_projetee(A, b, couts, mu=1.0, critere="deplacment")


def test_le_point_de_depart_est_ramene_dans_le_domaine(deux_conduites_paralleles):
    """Un q_initial négatif doit être projeté avant la première itération."""
    A, b, couts = deux_conduites_paralleles
    q, _ = descente_projetee(A, b, couts, mu=100.0, q_initial=np.array([-50.0, -50.0]),
                             max_iterations=50_000)

    assert np.all(q >= 0.0)
    assert cout(q, couts) > 0.0
