"""Résolution du problème d'optimisation sur un ensemble de scénarios.

Responsable : M5.
Dépend de : Étape 5 (scénarios de M3/M5) et Étape 9 (solveur validé).
Alimente : M6 pour la comparaison à la stratégie de référence.
Étape 10 du pipeline.

Le sujet demande de tester q* sur des situations variées, pas seulement sur la
demande moyenne. C'est ce que ce module industrialise.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.graph.build_graph import construire_second_membre, vecteur_couts
from src.optimization.gradient_descent import descente_projetee, pas_maximal_theorique
from src.optimization.objective import cout, violation_contrainte
from src.probability.demand_model import parametres_demande


@dataclass(frozen=True)
class ResultatScenario:
    """Ce qu'on retient d'un scénario résolu.

    On conserve à la fois ``cout_technique`` et ``violation`` : une solution
    peut sembler très bon marché simplement parce qu'elle ne respecte pas la
    conservation des flux. Présenter le coût sans la violation associée
    donnerait une comparaison trompeuse.
    """

    indice: int
    demandes: np.ndarray
    q_optimal: np.ndarray
    cout_technique: float
    violation: float
    n_iterations: int
    a_converge: bool


def resoudre_scenario(reseau, A: np.ndarray, demandes: np.ndarray, mu: float, **options) -> ResultatScenario:
    """Résout le problème pénalisé pour un scénario de demande donné.

    Enchaînement : ``construire_second_membre`` pour obtenir b, puis
    ``descente_projetee``, puis calcul des métriques.
    """
    demandes = np.asarray(demandes, dtype=float)
    b = construire_second_membre(reseau, demandes)
    couts = vecteur_couts(reseau)

    q, historique = descente_projetee(A, b, couts, mu, **options)

    return ResultatScenario(
        indice=int(options.pop('indice', 0)) if 'indice' in options else 0,
        demandes=demandes,
        q_optimal=q,
        cout_technique=cout(q, couts),
        violation=violation_contrainte(q, A, b),
        n_iterations=historique.n_iterations,
        a_converge=historique.a_converge,
    )


def resoudre_tous(
    reseau, A: np.ndarray, scenarios: np.ndarray, mu: float, **options
) -> list[ResultatScenario]:
    """Résout le problème sur chaque scénario d'un jeu Monte-Carlo.

    Args:
        scenarios: tableau (N, |quartiers|) issu de ``generer_scenarios``.

    Returns:
        Un résultat par scénario, dans l'ordre.

    Attention au coût de calcul : N scénarios × k itérations de descente. Sur
    N = 10 000, une descente lente devient une expérience qui ne tourne plus.
    Si le temps devient un obstacle, le réduire en resserrant la tolérance ou
    en partant d'un q_initial pertinent, mais jamais en baissant N en silence, ce
    qui dégraderait la fiabilité statistique sans que le rapport le signale
    (erreur listée en section 14 du plan).
    """
    scenarios = np.asarray(scenarios, dtype=float)
    couts = vecteur_couts(reseau)
    seconds_membres = np.array(
        [construire_second_membre(reseau, demandes) for demandes in scenarios]
    )

    Q, iterations, converges = descente_projetee_par_lot(
        A, seconds_membres, couts, mu, **options
    )

    return [
        ResultatScenario(
            indice=indice,
            demandes=scenarios[indice],
            q_optimal=Q[indice],
            cout_technique=cout(Q[indice], couts),
            violation=violation_contrainte(Q[indice], A, seconds_membres[indice]),
            n_iterations=int(iterations[indice]),
            a_converge=bool(converges[indice]),
        )
        for indice in range(scenarios.shape[0])
    ]


def descente_projetee_par_lot(
    A: np.ndarray,
    seconds_membres: np.ndarray,
    couts: np.ndarray,
    mu: float,
    eta: float | None = None,
    tolerance: float = 1e-8,
    max_iterations: int = 100_000,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fait avancer tous les scénarios en même temps dans la descente projetée.

    Même algorithme que ``descente_projetee``, même pas, même règle de mise à
    jour, même projection à chaque itération, même critère d'arrêt sur le
    déplacement. La seule différence tient à la mise en œuvre : les N scénarios
    voyagent dans des tableaux de forme (N, |E|) au lieu de passer un par un.

    Aucun raccourci mathématique n'est pris, et le test
    ``test_le_lot_donne_le_meme_resultat_que_la_boucle`` compare les deux
    versions sur le vrai réseau.

    Pourquoi cette version existe. La descente demande environ 8000 tours pour
    converger à µ = 100, quel que soit le nombre de scénarios. En boucle, chaque
    scénario paie ses 8000 passages dans l'interpréteur Python, soit près d'une
    seconde par scénario et un quart d'heure pour les mille scénarios de
    l'Expérience 2. En lot, ce sont les mêmes 8000 tours, mais chacun traite les
    mille scénarios d'un coup dans deux produits de matrices.

    Un scénario qui atteint le seuil avant les autres continue d'être mis à jour
    jusqu'à la fin de la boucle. Ça ne le déplace pas : il est arrivé au point
    fixe de l'itération projetée, donc un tour de plus le laisse où il est.

    Args:
        A: matrice d'incidence, forme (|V|, |E|).
        seconds_membres: les b empilés, forme (N, |V|).
        couts: vecteur des c_e, longueur |E|.
        mu: paramètre de pénalisation.
        eta: pas d'apprentissage. Par défaut la moitié de la borne 2/L, comme
            dans ``descente_projetee``.
        tolerance: seuil sur le déplacement, appliqué scénario par scénario.
        max_iterations: garde-fou.

    Returns:
        Le triplet (Q, iterations, converges), de formes (N, |E|), (N,) et (N,).
    """
    A = np.asarray(A, dtype=float)
    seconds_membres = np.asarray(seconds_membres, dtype=float)
    couts = np.asarray(couts, dtype=float)

    if eta is None:
        eta = 0.5 * pas_maximal_theorique(A, couts, mu)

    n_scenarios = seconds_membres.shape[0]
    Q = np.zeros((n_scenarios, A.shape[1]), dtype=float)
    iterations = np.zeros(n_scenarios, dtype=int)
    converges = np.zeros(n_scenarios, dtype=bool)

    for k in range(max_iterations):
        # residu vaut Aq - b pour chaque scenario, ecrit en lignes.
        residu = Q @ A.T - seconds_membres
        gradients = 2.0 * couts * Q + 2.0 * mu * (residu @ A)

        Q_suivant = np.maximum(Q - eta * gradients, 0.0)
        deplacements = np.linalg.norm(Q_suivant - Q, axis=1)
        Q = Q_suivant

        iterations[~converges] = k + 1
        converges |= deplacements < tolerance

        if converges.all():
            break

    iterations[~converges] = max_iterations
    return Q, iterations, converges


def scenarios_de_stress(reseau, quantile: float = 0.95) -> np.ndarray:
    """Construit des scénarios extrêmes plutôt que typiques.

    La section 10 du plan demande des scénarios moyen, favorable et
    défavorable. Un plan de distribution qui ne tient que sur la demande
    moyenne n'a aucun intérêt opérationnel : c'est sur les pointes que le
    réseau casse.

    Args:
        quantile: niveau de sévérité, 0.95 pour une demande haute.
    """
    from scipy import stats

    mu, sigma = parametres_demande(reseau)
    z = float(stats.norm.ppf(quantile))

    # Scenario de stress *marginal* : chaque quartier est pousse a son propre
    # quantile. Ce n'est pas le quantile de la demande totale, qui serait plus
    # faible puisque les ecarts ne se cumulent jamais parfaitement. Le rapport
    # doit dire laquelle des deux lectures il retient.
    return mu + z * sigma
