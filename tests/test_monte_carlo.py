"""Garde-fous sur la simulation Monte-Carlo et l'orchestration, périmètre M5.

Deux choses sont vérifiées ici. D'abord que les statistiques agrégées disent la
vérité, en particulier la décroissance de l'erreur en 1/√N, qui est le résultat
théorique central de cette partie du projet.

Ensuite que la descente vectorisée sur tous les scénarios donne le même
résultat que la boucle scénario par scénario. Cette version en lot existe pour
une raison de temps de calcul, pas de mathématiques, et rien ne garantirait
autrement qu'elle n'a pas introduit un écart en chemin.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from data.generate_network import charger_reseau
from src.graph.build_graph import (
    construire_matrice_incidence,
    construire_second_membre,
    vecteur_couts,
)
from src.optimization.gradient_descent import descente_projetee
from src.probability.monte_carlo import (
    agreger,
    convergence_par_taille,
    erreur_estimation,
    generer_scenarios,
)
from src.simulation.run_scenarios import (
    descente_projetee_par_lot,
    resoudre_tous,
    scenarios_de_stress,
)

CONFIG = Path(__file__).resolve().parents[1] / "data" / "network_config.json"


@pytest.fixture(scope="module")
def reseau():
    return charger_reseau(CONFIG)


@pytest.fixture(scope="module")
def matrice(reseau):
    return construire_matrice_incidence(reseau)


def test_les_scenarios_sont_reproductibles(reseau):
    """Deux appels avec la même graine doivent donner exactement les mêmes tirages.

    Sans cette garantie, aucun chiffre du rapport n'est reproductible par un
    correcteur qui relance le code.
    """
    premier = generer_scenarios(reseau, 200, graine=7)
    second = generer_scenarios(reseau, 200, graine=7)
    autre = generer_scenarios(reseau, 200, graine=8)

    assert premier == pytest.approx(second)
    assert not np.allclose(premier, autre)


def test_les_scenarios_retrouvent_les_parametres_declares(reseau):
    """Sur 20 000 tirages, moyennes et écarts-types doivent tomber juste."""
    from src.probability.demand_model import parametres_demande

    mu, sigma = parametres_demande(reseau)
    scenarios = generer_scenarios(reseau, 20_000)

    assert np.mean(scenarios, axis=0) == pytest.approx(mu, abs=0.3)
    assert np.std(scenarios, axis=0, ddof=1) == pytest.approx(sigma, rel=0.05)


def test_erreur_estimation_decroit_en_un_sur_racine_de_n():
    """σ̂/√N : quadrupler le nombre de tirages divise l'erreur par deux.

    C'est la conséquence contre-intuitive qui justifie le dimensionnement retenu,
    et qui doit être dite telle quelle en soutenance.
    """
    assert erreur_estimation(10.0, 100) == pytest.approx(1.0)
    assert erreur_estimation(10.0, 400) == pytest.approx(0.5)
    assert erreur_estimation(10.0, 10_000) == pytest.approx(0.1)


def test_convergence_par_taille_montre_la_decroissance(reseau):
    """L'erreur standard doit être divisée par √10 à chaque palier."""
    totaux = generer_scenarios(reseau, 10_000).sum(axis=1)
    resultats = convergence_par_taille(totaux, tailles=(100, 1_000, 10_000))

    erreurs = [resultats[taille].erreur_standard for taille in (100, 1_000, 10_000)]

    assert erreurs[0] / erreurs[1] == pytest.approx(np.sqrt(10.0), rel=0.25)
    assert erreurs[1] / erreurs[2] == pytest.approx(np.sqrt(10.0), rel=0.25)


def test_agreger_refuse_un_echantillon_trop_petit():
    """La variance corrigée demande au moins deux tirages, sinon on divise par zéro."""
    with pytest.raises(ValueError, match="au moins 2 tirages"):
        agreger(np.array([1.0]))


def test_convergence_par_taille_refuse_de_depasser_la_population():
    """Demander 10 000 tirages sur une population de 100 doit lever.

    Retourner silencieusement un résultat sur moins de tirages que demandé
    donnerait une erreur d'estimation fausse dans le rapport.
    """
    with pytest.raises(ValueError, match="Générer davantage de tirages"):
        convergence_par_taille(np.zeros(100), tailles=(100, 10_000))


def test_le_lot_donne_le_meme_resultat_que_la_boucle(reseau, matrice):
    """La vectorisation ne doit rien changer au résultat, seulement au temps passé.

    On compare sur cinq scénarios réels. La tolérance de comparaison est plus
    lâche que la tolérance d'arrêt du solveur : les deux versions s'arrêtent au
    même point fixe, mais pas exactement au même tour, donc elles ne rendent pas
    des flottants identiques au bit près.
    """
    couts = vecteur_couts(reseau)
    scenarios = generer_scenarios(reseau, 5)

    par_lot = resoudre_tous(reseau, matrice, scenarios, mu=100.0, tolerance=1e-8)

    for resultat, demandes in zip(par_lot, scenarios):
        b = construire_second_membre(reseau, demandes)
        attendu, _ = descente_projetee(
            matrice, b, couts, 100.0, tolerance=1e-8, max_iterations=100_000
        )
        assert resultat.q_optimal == pytest.approx(attendu, abs=1e-4)


def test_tous_les_debits_resolus_sont_positifs(reseau, matrice):
    """La contrainte q ≥ 0 doit tenir sur chaque scénario, sans exception."""
    scenarios = generer_scenarios(reseau, 50)
    resultats = resoudre_tous(reseau, matrice, scenarios, mu=100.0, tolerance=1e-8)

    assert all(np.all(resultat.q_optimal >= 0.0) for resultat in resultats)
    assert all(resultat.a_converge for resultat in resultats)


def test_la_violation_baisse_quand_mu_monte_sur_les_scenarios(reseau, matrice):
    """Section 6.2 du Membre 4, vérifiée cette fois sur un jeu de scénarios."""
    scenarios = generer_scenarios(reseau, 20)

    moyennes = []
    for mu in (10.0, 100.0, 1000.0):
        resultats = resoudre_tous(reseau, matrice, scenarios, mu=mu, tolerance=1e-8)
        moyennes.append(float(np.mean([r.violation for r in resultats])))

    assert moyennes == sorted(moyennes, reverse=True)


def test_scenarios_de_stress_depassent_la_demande_moyenne(reseau):
    """Un scénario de stress à 95 % doit placer chaque quartier au-dessus de sa moyenne."""
    from src.probability.demand_model import parametres_demande

    mu, _ = parametres_demande(reseau)
    stress = scenarios_de_stress(reseau, quantile=0.95)

    assert np.all(stress > mu)
    assert np.all(scenarios_de_stress(reseau, quantile=0.5) == pytest.approx(mu))


def test_le_lot_signale_les_scenarios_non_converges(reseau, matrice):
    """Un budget d'itérations trop court doit se voir, pas passer inaperçu."""
    couts = vecteur_couts(reseau)
    scenarios = generer_scenarios(reseau, 3)
    seconds_membres = np.array(
        [construire_second_membre(reseau, demandes) for demandes in scenarios]
    )

    _, iterations, converges = descente_projetee_par_lot(
        matrice, seconds_membres, couts, mu=1000.0, tolerance=1e-10, max_iterations=50
    )

    assert not converges.any()
    assert np.all(iterations == 50)
