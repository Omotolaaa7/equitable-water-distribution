"""Garde-fous sur le modèle de demande, périmètre M3.

Ces tests existent pour une raison précise. Pendant plusieurs jours, le modèle
de demande a tourné sur des corrélations codées en dur qui différaient de celles
déclarées par le Membre 1 sur 15 paires de quartiers sur 28. Rien ne l'a
signalé, parce qu'aucune vérification ne confrontait le code au fichier de
configuration.

L'écart n'était pas cosmétique : selon la version retenue, la probabilité que la
demande totale dépasse l'offre passait de un jour sur 116 à un jour sur 56.

Contrairement aux autres fichiers de ``tests/``, ceux-ci ne sont pas ignorés :
le code qu'ils vérifient est écrit.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from data.generate_network import charger_reseau
from src.probability import demand_model as dm

CONFIG = Path(__file__).resolve().parents[1] / "data" / "network_config.json"


@pytest.fixture(scope="module")
def configuration() -> dict:
    """Le fichier du Membre 1, lu tel quel."""
    with open(CONFIG, encoding="utf-8") as fichier:
        return json.load(fichier)


@pytest.fixture(scope="module")
def reseau():
    """Le même fichier, chargé sous forme d'objet par le code du Membre 1."""
    return charger_reseau(CONFIG)


@pytest.fixture(scope="module")
def correlations_declarees(configuration) -> dict:
    """Les corrélations telles que le Membre 1 les déclare, indexées par paire."""
    declarees = {}
    for entree in configuration["correlations_voisinage"]:
        a, b = entree["quartiers"]
        declarees[frozenset((a, b))] = float(entree["rho"])
    return declarees


def test_mu_et_sigma_viennent_du_fichier(configuration, reseau):
    """Les paramètres lus doivent être ceux du fichier, pas des valeurs internes.

    Le test passe par les deux chemins d'entrée acceptés, l'objet réseau et le
    dictionnaire brut, parce que c'est exactement là que le repli silencieux se
    produisait.
    """
    attendus_mu = [float(q["mu"]) for q in configuration["noeuds"]["quartiers"]]
    attendus_sigma = [float(q["sigma"]) for q in configuration["noeuds"]["quartiers"]]

    for source in (reseau, configuration):
        mu, sigma = dm.parametres_demande(source)
        assert np.allclose(mu, attendus_mu)
        assert np.allclose(sigma, attendus_sigma)


def test_correlations_identiques_a_celles_declarees(reseau, configuration, correlations_declarees):
    """Aucune paire ne doit s'écarter de ce que le Membre 1 déclare.

    C'est le test qui manquait. Il compare paire par paire, et il échoue si une
    seule valeur diverge.
    """
    identifiants = [q["id"] for q in configuration["noeuds"]["quartiers"]]

    for source in (reseau, configuration):
        _, sigma = dm.parametres_demande(source)
        covariance = dm.matrice_covariance(source)
        correlation = covariance / np.outer(sigma, sigma)

        ecarts = []
        for i, a in enumerate(identifiants):
            for j, b in enumerate(identifiants):
                if j <= i:
                    continue
                attendu = correlations_declarees.get(frozenset((a, b)), 0.0)
                obtenu = correlation[i, j]
                if abs(attendu - obtenu) > 1e-9:
                    ecarts.append(f"{a}-{b} : déclaré {attendu}, obtenu {obtenu}")

        assert not ecarts, "Corrélations divergentes :\n" + "\n".join(ecarts)


def test_structure_inconnue_leve_au_lieu_de_se_rabattre(reseau):
    """Une configuration illisible doit lever, jamais retomber sur des valeurs internes.

    C'est le comportement qui a permis au problème de passer inaperçu. Un repli
    muet fait travailler tout le projet sur des chiffres absents du rapport.
    """
    with pytest.raises(ValueError, match="Aucun quartier lisible"):
        dm.parametres_demande({"une_cle_inattendue": 1})

    with pytest.raises(TypeError, match="Type de réseau non reconnu"):
        dm.parametres_demande(42)


def test_covariance_symetrique_et_definie_positive(reseau):
    """Sans quoi la matrice ne décrit aucune loi gaussienne réelle.

    Une matrice assemblée paire par paire n'est pas automatiquement définie
    positive, et l'échantillonnage échouerait plus loin sans dire pourquoi.
    """
    covariance = dm.matrice_covariance(reseau)
    assert np.allclose(covariance, covariance.T)
    assert np.all(np.linalg.eigvalsh(covariance) > 0)


def test_diagonale_de_la_covariance_vaut_les_variances(reseau):
    """Σ_ii doit valoir σ_i², puisque ρ_ii vaut 1 par construction."""
    _, sigma = dm.parametres_demande(reseau)
    covariance = dm.matrice_covariance(reseau)
    assert np.allclose(np.diag(covariance), sigma ** 2)


def test_les_tirages_retrouvent_les_parametres_declares(reseau):
    """Contrôle de bout en bout du générateur.

    Sur 20 000 tirages, les moyennes, les écarts-types et les corrélations
    empiriques doivent retrouver les valeurs déclarées. Un écart important
    signale une erreur dans la covariance ou dans l'échantillonnage, et vaut
    mieux d'être vu ici que six expériences plus loin.

    Les tolérances sont volontairement lâches : l'erreur d'estimation
    Monte-Carlo décroît en 1/√N, donc sur 20 000 tirages il reste du bruit.
    """
    mu, sigma = dm.parametres_demande(reseau)
    covariance = dm.matrice_covariance(reseau)
    generateur = np.random.default_rng(42)

    echantillon = dm.echantillonner(mu, covariance, 20_000, generateur)

    assert np.allclose(dm.estimateur_moyenne(echantillon), mu, atol=0.3)
    assert np.allclose(np.sqrt(dm.estimateur_variance(echantillon)), sigma, rtol=0.05)

    correlation_declaree = covariance / np.outer(sigma, sigma)
    assert np.allclose(dm.correlations_empiriques(echantillon), correlation_declaree, atol=0.05)


def test_regle_spatiale_se_recalcule_depuis_la_topologie(reseau, correlations_declarees):
    """La règle proposée par le Membre 3, déduite du graphe plutôt qu'écrite à la main.

    Les paires de voisins directs qu'elle trouve doivent être exactement celles
    que le Membre 1 déclare. Les deux membres s'accordent donc sur *quelles*
    paires sont voisines, et divergent seulement sur la valeur de ρ et sur le
    fait de corréler ou non les quartiers à deux conduites d'écart.
    """
    entrees = dm.paires_voisinage_depuis_topologie(reseau)
    voisins_directs = {
        frozenset(e["quartiers"]) for e in entrees if e["rho"] == pytest.approx(0.40)
    }
    assert voisins_directs == set(correlations_declarees)
