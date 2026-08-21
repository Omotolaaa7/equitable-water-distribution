"""Expérience 4 — Vérification empirique de la borne de convergence.

Responsable : M5, interprétation avec M4.
Dépend de : la borne théorique η < 2/L établie par M4 à partir du L de M2.

Première des deux confrontations théorie/expérience exigées par le sujet.

    Objectif    Confronter la borne théorique sur le pas au comportement
                réellement observé.
    Paramètres  Plusieurs η, certains sous 2/L, d'autres au-delà.
    Données     Réseau synthétique.
    Méthode     Lancer la descente projetée pour chaque η, suivre la norme du
                gradient et J(q_k) au fil des itérations.
    Métriques   ‖∇J(q_k)‖ et J(q_k) en fonction de k.
    Attendu     Convergence stable sous la borne, oscillation ou divergence
                au-delà.
    Graphique   Courbes de J(q_k) en fonction de k, une par η.

Protocole recommandé : encadrer franchement le seuil, par exemple
η ∈ {0.1, 0.5, 0.9, 1.1, 1.5} × (2/L). Un balayage qui reste entièrement d'un
côté du seuil ne démontre rien.

Deux précautions de mise en œuvre :

- prévoir un garde-fou de dépassement numérique. Au-delà de 2/L, J(q_k) part en
  overflow en quelques dizaines d'itérations, et le script doit s'arrêter
  proprement plutôt que de remplir la sortie de ``inf`` et de ``nan`` ;
- tracer J en échelle logarithmique. Sur une échelle linéaire, les cas
  divergents écrasent visuellement les cas convergents et la figure ne montre
  plus rien.

L'erreur à ne pas commettre, listée en section 14 : présenter une courbe qui
descend comme preuve de convergence. Ce qui est démontré ici, c'est le lien
entre la constante de Lipschitz calculée à l'Étape 3 et le comportement
observé de part et d'autre du seuil — pas le simple fait que ça descende.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M5 — Expérience 4.")


if __name__ == "__main__":
    main()
