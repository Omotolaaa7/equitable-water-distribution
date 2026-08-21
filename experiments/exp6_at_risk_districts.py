"""Expérience 6 — Identification des quartiers à risque.

Responsable : M3, avec M5 pour l'exécution.
Dépend de : les estimateurs et intervalles de confiance de l'Étape 4.

Exploite le volet statistique pour enrichir l'interprétation. C'est
l'expérience qui relie le travail probabiliste au terrain : elle produit
l'information qu'un ingénieur réseau peut réellement utiliser.

    Objectif    Repérer les quartiers dont la demande s'écarte régulièrement
                des prévisions.
    Paramètres  Historique simulé de demande sur plusieurs périodes.
    Données     Tirages répétés avec un biais volontaire sur certains quartiers.
    Méthode     Calcul d'intervalles de confiance et de corrélations,
                comparaison à la demande prévue.
    Métriques   Fréquence de dépassement de l'IC par quartier.
    Attendu     Identification des quartiers à demande atypique.
    Graphique   Tableau récapitulatif par quartier.

Point de méthode à ne pas manquer : le biais est introduit *volontairement* sur
certains quartiers. Ce sont eux la vérité terrain de l'expérience, et le
critère de réussite est que la méthode les retrouve — sans lever de fausse
alerte sur les quartiers non biaisés. Le taux de fausses alertes attendu sur un
IC à 95 % est d'environ 5 % : c'est le repère par rapport auquel toute
fréquence mesurée doit être lue.

Interprétation à faire, et qui est le vrai intérêt de l'expérience : relier ces
quartiers à la robustesse de q*. Un quartier à demande atypique *et* situé en
bout de réseau, relié par une seule conduite, cumule un risque statistique et
un risque structurel. C'est le point où le volet probabiliste et le volet
graphe se rejoignent, et c'est le genre de synthèse que la grille récompense.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M3 avec M5 — Expérience 6.")


if __name__ == "__main__":
    main()
