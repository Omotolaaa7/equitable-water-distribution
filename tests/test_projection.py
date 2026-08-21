"""Garde-fous sur la projection et la descente, périmètre M5.

Ces tests restent inactifs tant que le jalon de la section 16 n'est pas
franchi. Les écrire avant de coder le solveur est en revanche utile : ils
fixent noir sur blanc ce que le solveur devra vérifier.
"""

from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Bloqué par le jalon section 16.")
def test_projection_ne_renvoie_jamais_de_negatif():
    """P(q) ≥ 0 pour tout q, y compris massivement négatif."""


@pytest.mark.skip(reason="Bloqué par le jalon section 16.")
def test_projection_est_idempotente():
    """P(P(q)) = P(q).

    Propriété caractéristique d'une projection. Sa violation signalerait que
    la fonction fait autre chose qu'une projection : une remise à l'échelle,
    par exemple.
    """
