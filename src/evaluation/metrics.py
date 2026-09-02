"""Métriques de comparaison entre stratégies de distribution.

Responsable : M6, en collaboration avec M5.
Étape 11 du pipeline.

Trois familles de métriques, qui répondent à trois questions distinctes et ne
doivent pas être confondues dans le tableau final :

- **coût technique** : combien coûte l'acheminement ?
- **violation de contrainte** : la conservation des flux est-elle respectée ?
- **équité** : tous les quartiers sont-ils servis de façon comparable ?

L'équité est la plus délicate : le sujet parle de « distribuer équitablement »,
mais la fonction objectif Σ c_e q_e² ne contient aucun terme d'équité. Le
rapport doit assumer cette tension au lieu de la masquer : l'équité de q* est
un effet indirect de la pénalisation quadratique, qui répartit l'effort au lieu
de le concentrer, et non un objectif explicite du modèle. C'est une limite du
travail, et la section « Limites » du rapport est notée.
"""

from __future__ import annotations

import numpy as np


def cout_total(q: np.ndarray, couts: np.ndarray) -> float:
    """Coût technique Σ c_e q_e² d'une distribution.

    Métrique de comparaison principale entre la référence et q*.
    """
    q = np.asarray(q, dtype=float)
    couts = np.asarray(couts, dtype=float)
    if q.shape != couts.shape:
        raise ValueError("q et couts doivent avoir la même forme.")
    return float(np.sum(couts * q ** 2))


def taux_de_satisfaction(reseau, q: np.ndarray, demandes: np.ndarray) -> np.ndarray:
    """Part de sa demande effectivement reçue par chaque quartier.

        s_i = (eau reçue au quartier i) / D_i

    Un s_i supérieur à 1 signale un sur-approvisionnement, inférieur à 1 un
    quartier sous-servi. C'est la grandeur sur laquelle se lit l'équité.

    Returns:
        Vecteur des s_i, longueur |quartiers|.
    """
    demandes = np.asarray(demandes, dtype=float)
    q = np.asarray(q, dtype=float)
    if demandes.shape != (len(reseau.quartiers),):
        raise ValueError("demandes doit contenir une valeur par quartier.")
    if q.shape != (len(reseau.conduites),):
        raise ValueError("q doit contenir une valeur par conduite.")
    recu = np.zeros(len(reseau.quartiers), dtype=float)
    index = {quartier.identifiant: i for i, quartier in enumerate(reseau.quartiers)}
    for debit, conduite in zip(q, reseau.conduites):
        if conduite.cible in index:
            recu[index[conduite.cible]] += debit
        if conduite.source in index:
            recu[index[conduite.source]] -= debit
    return np.divide(recu, demandes, out=np.zeros_like(recu), where=demandes > 0)


def ecart_type_satisfaction(taux: np.ndarray) -> float:
    """Indicateur d'équité : dispersion des taux de satisfaction.

    Un écart-type faible signifie que tous les quartiers sont servis de façon
    comparable, quelle que soit la qualité absolue du service. À lire toujours
    conjointement avec la moyenne des taux : un réseau qui sous-sert tout le
    monde de façon identique obtient un excellent score d'équité et reste un
    mauvais réseau.
    """
    taux = np.asarray(taux, dtype=float)
    if taux.ndim != 1 or taux.size == 0:
        raise ValueError("taux doit être un vecteur non vide.")
    return float(np.std(taux, ddof=0))


def quartier_le_moins_servi(reseau, taux: np.ndarray) -> tuple[str, float]:
    """Identifie le quartier au plus faible taux de satisfaction.

    Lecture minimax de l'équité, complémentaire de l'écart-type : elle répond à
    « à quel point le plus mal servi est-il mal servi ? » plutôt qu'à « les
    écarts sont-ils réduits ? ». Les deux lectures peuvent se contredire, et
    c'est justement ce qui rend leur confrontation intéressante dans le rapport.
    """
    taux = np.asarray(taux, dtype=float)
    if taux.shape != (len(reseau.quartiers),):
        raise ValueError("taux doit contenir une valeur par quartier.")
    indice = int(np.argmin(taux))
    return reseau.quartiers[indice].identifiant, float(taux[indice])


def violation_conservation(q: np.ndarray, A: np.ndarray, b: np.ndarray) -> float:
    """Norme du résidu ‖Aq − b‖ pour une distribution quelconque.

    S'applique aussi bien à q* qu'à la stratégie de référence. La référence n'a
    aucune raison de satisfaire la conservation : la comparer sur ce critère
    fait partie de l'argumentaire.
    """
    q = np.asarray(q, dtype=float)
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.linalg.norm(A @ q - b))


def depassements_de_capacite(reseau, q: np.ndarray) -> dict[str, float]:
    """Conduites dont le débit dépasse la capacité déclarée.

    Le modèle d'optimisation retenu n'impose *pas* q_e ≤ cap_e, seulement
    q ≥ 0. Les capacités du fichier de configuration sont donc, en l'état, des
    données descriptives et non des contraintes actives.

    Cette fonction sert à vérifier a posteriori si q* les respecte. Si des
    dépassements apparaissent, deux issues, toutes deux acceptables à condition
    d'être argumentées : les signaler comme limite du modèle, ou ajouter un
    second terme de pénalisation. Ce qui ne serait pas acceptable, c'est de ne
    pas regarder.

    Returns:
        Les dépassements par conduite, vide si toutes les capacités sont tenues.
    """
    q = np.asarray(q, dtype=float)
    if q.shape != (len(reseau.conduites),):
        raise ValueError("q doit contenir une valeur par conduite.")
    depassements = {}
    for debit, conduite in zip(q, reseau.conduites):
        excedent = float(debit - conduite.capacite)
        if excedent > 0:
            depassements[f"{conduite.source}-{conduite.cible}"] = excedent
    return depassements
