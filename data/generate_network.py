"""Génération et validation du réseau synthétique.

Responsable : M1 (topologie, hypothèses physiques, orientation des arêtes).
Dépendances : aucune, c'est le point de départ du projet.
Étape 1 du pipeline (section 2 du plan de projet).

Le sujet n'exige pas de données réelles. La section 5.2 du plan recommande
explicitement un jeu synthétique, à condition que sa construction soit
expliquée et défendue dans le rapport : 8 à 15 quartiers, 2 à 3 réservoirs,
σ_i entre 10 % et 30 % de µ_i, corrélation modérée entre quartiers proches.

Ce module a deux usages distincts :

1. charger et *valider* ``data/network_config.json``, le réseau de référence
   figé par M1, utilisé par toutes les expériences sauf la cinquième ;
2. générer des *variantes de maillage* du même réseau (de très peu de
   conduites à un réseau bien maillé) pour l'Expérience 5, qui mesure l'effet
   du maillage sur le conditionnement de A.

Ces variantes ne sont pas décoratives : sans elles, l'Expérience 5 n'a rien à
comparer, et la deuxième confrontation théorie/expérience exigée par le sujet
tombe.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path

import networkx as nx


@dataclass(frozen=True)
class Conduite:
    """Une arête orientée du réseau.

    L'orientation porte une convention physique que M1 doit fixer et défendre :
    un débit q_e positif signifie que l'eau circule de ``source`` vers
    ``cible``. Un débit négatif, si le modèle l'autorisait, signifierait un
    écoulement inverse, mais la contrainte q ≥ 0 l'interdit, ce qui revient à
    supposer que le sens d'écoulement de chaque conduite est connu d'avance.
    C'est une hypothèse de modélisation à assumer explicitement dans le rapport.
    """

    source: str
    cible: str
    capacite: float
    cout: float


@dataclass(frozen=True)
class Quartier:
    """Un nœud de demande, de loi D_i ~ N(µ_i, σ_i²)."""

    identifiant: str
    nom: str
    mu: float
    sigma: float


@dataclass(frozen=True)
class Reservoir:
    """Un nœud source, d'offre disponible fixée."""

    identifiant: str
    nom: str
    offre: float


@dataclass(frozen=True)
class Reseau:
    """Le réseau complet : ce que M1 livre au reste du groupe.

    C'est l'objet qui circule dans tout le projet. Tant qu'il n'est pas figé et
    validé collectivement, M2 ne peut pas construire A, et rien ne démarre.
    """

    reservoirs: tuple[Reservoir, ...]
    quartiers: tuple[Quartier, ...]
    conduites: tuple[Conduite, ...]
    correlations_voisinage: tuple[dict, ...]
    hyperparametres: dict

    @property
    def noeuds(self) -> tuple[str, ...]:
        """Tous les nœuds V, réservoirs d'abord puis quartiers.

        L'ordre compte : il fixe l'ordre des lignes de la matrice d'incidence A
        et donc l'ordre des composantes de b. M2 et M4 doivent lire cet ordre
        ici plutôt que de le redéfinir de leur côté.
        """
        return tuple(r.identifiant for r in self.reservoirs) + tuple(
            q.identifiant for q in self.quartiers
        )


def _reseau_depuis_dict(data: dict) -> Reseau:
    """Construit un ``Reseau`` à partir du dict JSON déjà chargé.

    Fonction interne, séparée de ``charger_reseau`` pour être réutilisable par
    ``generer_variantes_de_maillage`` sans repasser par le disque.
    """
    reservoirs = tuple(
        Reservoir(
            identifiant=r["id"],
            nom=r.get("nom", r["id"]),
            offre=r["offre_max"],
        )
        for r in data["noeuds"]["reservoirs"]
    )
    quartiers = tuple(
        Quartier(
            identifiant=q["id"],
            nom=q.get("nom", q["id"]),
            mu=q["mu"],
            sigma=q["sigma"],
        )
        for q in data["noeuds"]["quartiers"]
    )
    conduites = tuple(
        Conduite(
            source=c["de"],
            cible=c["vers"],
            capacite=c["capacite"],
            cout=c["cout_unitaire"],
        )
        for c in data["conduites"]
    )
    correlations_voisinage = tuple(data.get("correlations_voisinage", ()))
    hyperparametres = dict(data.get("hyperparametres", {}))

    return Reseau(
        reservoirs=reservoirs,
        quartiers=quartiers,
        conduites=conduites,
        correlations_voisinage=correlations_voisinage,
        hyperparametres=hyperparametres,
    )


def charger_reseau(chemin: Path | str) -> Reseau:
    """Charge le réseau depuis un fichier de configuration JSON.

    Args:
        chemin: chemin vers ``network_config.json``.

    Returns:
        Le réseau, prêt à être passé à ``src.graph.build_graph``.

    Raises:
        ValueError: si la configuration est incohérente (voir ``valider_reseau``).
    """
    chemin = Path(chemin)
    data = json.loads(chemin.read_text(encoding="utf-8"))
    reseau = _reseau_depuis_dict(data)

    anomalies = valider_reseau(reseau)
    if anomalies:
        detail = "\n".join(f"- {a}" for a in anomalies)
        raise ValueError(
            f"Réseau invalide ({len(anomalies)} anomalie(s) détectée(s)) "
            f"dans {chemin} :\n{detail}"
        )
    return reseau


def valider_reseau(reseau: Reseau) -> list[str]:
    """Vérifie les invariants du réseau avant toute exploitation.

    Aucune de ces vérifications n'est cosmétique : chacune correspond à une
    hypothèse mathématique dont la violation casserait silencieusement une
    étape ultérieure.

    Invariants à contrôler :

    - tout coût c_e est strictement positif : c'est *exactement* la condition
      qui rend Σ c_e q_e² convexe (Étape 6). Un c_e nul ou négatif invaliderait
      la démonstration de convexité de M4 sans qu'aucune erreur ne se déclenche ;
    - toute capacité est strictement positive ;
    - toute conduite référence des nœuds qui existent ;
    - tout σ_i est strictement positif : un σ_i nul ferait de D_i une constante
      et viderait le volet Monte-Carlo de son sens ;
    - aucun quartier n'est orphelin (degré ≥ 1) ;
    - le rapport Σ offre / Σ µ_i est signalé s'il s'écarte de 1, puisque la
      conservation Aq = b n'est exactement satisfiable que si l'offre couvre
      la demande.

    Returns:
        La liste des anomalies détectées, vide si le réseau est sain.
    """
    anomalies: list[str] = []
    noeuds_connus = set(reseau.noeuds)

    if len(noeuds_connus) != len(reseau.reservoirs) + len(reseau.quartiers):
        anomalies.append(
            "Des identifiants de nœuds sont dupliqués entre réservoirs et "
            "quartiers (ou au sein d'un même groupe)."
        )

    for c in reseau.conduites:
        etiquette = f"{c.source}-{c.cible}"
        if c.cout <= 0:
            anomalies.append(
                f"Coût non strictement positif sur la conduite {etiquette} "
                f"(cout={c.cout}) : Σ c_e q_e² ne serait plus convexe."
            )
        if c.capacite <= 0:
            anomalies.append(
                f"Capacité non strictement positive sur la conduite "
                f"{etiquette} (capacite={c.capacite})."
            )
        if c.source not in noeuds_connus:
            anomalies.append(
                f"Conduite {etiquette} : nœud source inconnu '{c.source}'."
            )
        if c.cible not in noeuds_connus:
            anomalies.append(
                f"Conduite {etiquette} : nœud cible inconnu '{c.cible}'."
            )

    for q in reseau.quartiers:
        if q.sigma <= 0:
            anomalies.append(
                f"σ non strictement positif pour le quartier {q.identifiant} "
                f"(sigma={q.sigma}) : D_i deviendrait une constante."
            )
        if q.mu <= 0:
            anomalies.append(
                f"µ non strictement positif pour le quartier {q.identifiant} "
                f"(mu={q.mu})."
            )

    degres: dict[str, int] = {n: 0 for n in noeuds_connus}
    for c in reseau.conduites:
        if c.source in degres:
            degres[c.source] += 1
        if c.cible in degres:
            degres[c.cible] += 1
    for q in reseau.quartiers:
        if degres.get(q.identifiant, 0) == 0:
            anomalies.append(f"Quartier orphelin (degré 0) : {q.identifiant}.")

    # Le rapport Σ offre / Σ µ_i est *signalé* s'il s'écarte de 1, mais une
    # marge de l'ordre de 10-30 % est une hypothèse de conception assumée
    # (cf. hypothèses de M1), pas une erreur : seuls les écarts qui rendent
    # Aq=b structurellement infaisable (offre < demande) ou qui trahissent
    # probablement une erreur de saisie (offre > 2x la demande) sont
    # considérés comme des anomalies bloquantes.
    offre_totale = sum(r.offre for r in reseau.reservoirs)
    demande_totale = sum(q.mu for q in reseau.quartiers)
    if demande_totale <= 0:
        anomalies.append("Demande totale nulle ou négative : Σ µ_i <= 0.")
    else:
        ratio = offre_totale / demande_totale
        if ratio < 1.0:
            anomalies.append(
                f"Offre totale ({offre_totale}) < demande moyenne totale "
                f"({demande_totale}) : Aq=b ne sera pas satisfiable avec "
                f"q >= 0 dès que la demande réalisée dépasse µ, ratio="
                f"{ratio:.2f}."
            )
        elif ratio > 2.0:
            anomalies.append(
                f"Ratio offre/demande = {ratio:.2f} (offre={offre_totale}, "
                f"demande={demande_totale}) : marge inhabituellement grande, "
                f"probable erreur de configuration à vérifier."
            )

    graphe = nx.Graph()
    graphe.add_nodes_from(noeuds_connus)
    graphe.add_edges_from((c.source, c.cible) for c in reseau.conduites)
    if graphe.number_of_nodes() > 0 and not nx.is_connected(graphe):
        composantes = list(nx.connected_components(graphe))
        anomalies.append(
            f"Le graphe n'est pas connexe ({len(composantes)} composantes) : "
            f"Aq=b n'admet pas de solution cohérente sur l'ensemble du réseau."
        )

    return anomalies


def generer_variantes_de_maillage(
    reseau: Reseau, densites: tuple[float, ...]
) -> dict[float, Reseau]:
    """Produit des variantes du réseau à densité de maillage croissante.

    Pour l'Expérience 5 : on part du même ensemble de nœuds et de la même
    demande, et on fait varier le nombre de conduites entre quartiers. Le
    réseau le plus pauvre est un arbre couvrant, soit le minimum pour rester
    connexe ; le plus riche ajoute des conduites transversales.

    L'attente théorique, à confronter aux mesures : moins il y a de conduites
    reliant les quartiers entre eux, plus κ(AᵀA) est grand, et plus la descente
    de gradient met d'itérations à converger.

    Args:
        reseau: le réseau de référence.
        densites: proportions de conduites optionnelles conservées, dans [0, 1].
            0.0 donne un arbre couvrant, 1.0 le réseau complet.

    Returns:
        Une variante connexe par densité. La connexité doit être garantie pour
        chacune, faute de quoi le rang de A change de nature et la comparaison
        de conditionnement compare deux choses différentes.
    """
    for d in densites:
        if not 0.0 <= d <= 1.0:
            raise ValueError(f"Densité hors de [0, 1] : {d}")

    graphe = nx.Graph()
    graphe.add_nodes_from(reseau.noeuds)
    conduite_par_paire: dict[frozenset[str], Conduite] = {}
    for c in reseau.conduites:
        cle = frozenset((c.source, c.cible))
        conduite_par_paire[cle] = c
        graphe.add_edge(c.source, c.cible)

    if not nx.is_connected(graphe):
        raise ValueError(
            "Le réseau de référence n'est pas connexe : impossible d'en "
            "extraire un arbre couvrant pour l'Expérience 5."
        )

    arbre_couvrant = nx.minimum_spanning_tree(graphe)
    aretes_obligatoires = {frozenset(e) for e in arbre_couvrant.edges()}
    aretes_optionnelles = sorted(
        (cle for cle in conduite_par_paire if cle not in aretes_obligatoires),
        key=lambda cle: tuple(sorted(cle)),
    )

    variantes: dict[float, Reseau] = {}
    for d in densites:
        n_a_garder = math.ceil(d * len(aretes_optionnelles))
        aretes_retenues = aretes_obligatoires | set(aretes_optionnelles[:n_a_garder])
        conduites_variante = tuple(
            conduite_par_paire[cle] for cle in aretes_retenues
        )

        sous_graphe = nx.Graph()
        sous_graphe.add_nodes_from(reseau.noeuds)
        sous_graphe.add_edges_from(
            (c.source, c.cible) for c in conduites_variante
        )
        if not nx.is_connected(sous_graphe):
            raise AssertionError(
                f"Variante à densité {d} non connexe : incohérence interne, "
                f"l'arbre couvrant obligatoire aurait dû garantir la connexité."
            )

        variantes[d] = replace(reseau, conduites=conduites_variante)

    return variantes


if __name__ == "__main__":
    import sys

    chemin_config = Path(__file__).resolve().parents[2] / "data" / "network_config.json"
    reseau = charger_reseau(chemin_config)

    print(f"Réseau chargé : {len(reseau.reservoirs)} réservoir(s), "
          f"{len(reseau.quartiers)} quartier(s), {len(reseau.conduites)} conduite(s).")
    print("Aucune anomalie détectée (le chargement l'aurait signalé sinon).")

    variantes = generer_variantes_de_maillage(reseau, densites=(0.0, 0.25, 0.5, 0.75, 1.0))
    print("\nVariantes de maillage pour l'Expérience 5 :")
    for d, variante in sorted(variantes.items()):
        print(f"  densité={d:.2f} -> {len(variante.conduites)} conduite(s)")

    sys.exit(0)
