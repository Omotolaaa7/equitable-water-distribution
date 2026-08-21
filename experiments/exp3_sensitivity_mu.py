"""Expérience 3 : analyse de sensibilité du paramètre de pénalisation µ.

Responsable : M5, interprétation avec M4.
Dépend de : la dérivation de M4 sur le comportement asymptotique en µ.

Satisfait l'exigence (v) de la Contrainte méthodologique 3 : analyse de
sensibilité d'au moins un hyperparamètre. L'oublier est listé en section 14
parmi les erreurs à éviter.

    Objectif    Mesurer le compromis porté par µ.
    Paramètres  µ ∈ {1, 10, 100, 1000}.
    Données     Réseau synthétique, demande moyenne.
    Méthode     Résoudre le problème pénalisé pour chaque µ, observer
                convergence et violation résiduelle.
    Métriques   ‖Aq − b‖ finale, nombre d'itérations avant convergence,
                conditionnement effectif de 2C + 2µAᵀA.
    Attendu     La violation résiduelle décroît avec µ, mais la convergence
                ralentit quand µ devient grand.
    Graphique   Courbes de convergence superposées, une par µ.

Le compromis à expliciter, en lien direct avec la dérivation de l'Étape 7 :
augmenter µ resserre la contrainte d'égalité, mais alourdit la plus grande
valeur propre de la hessienne, donc dégrade κ(H), donc impose un pas plus petit
via η < 2/L, donc ralentit la convergence. Les deux effets ont la même origine
algébrique. Ce n'est pas une coïncidence expérimentale, et le rapport doit le
dire ainsi.

Attention au protocole : si η est recalculé à partir de 2/L pour chaque µ, le
nombre d'itérations mélange deux effets. Fixer le protocole retenu et le
documenter, sans quoi la courbe n'est pas interprétable.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401


def main() -> None:
    raise NotImplementedError("M5, Expérience 3.")


if __name__ == "__main__":
    main()
