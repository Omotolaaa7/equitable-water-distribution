"""Configuration pytest et fixtures partagées.

La boîte à outils du plan (section 10.3) retient pytest pour « donner une
garantie concrète que chaque brique fonctionne avant de l'assembler dans le
pipeline complet ». Ces tests ne sont pas un livrable noté en tant que tel :
ils protègent la rubrique « Implémentation & validation » (15 %) contre les
erreurs silencieuses — un facteur 2 oublié, un Aᵀ écrit A, un ddof par défaut.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))


@pytest.fixture
def reseau_minimal():
    """Un réseau volontairement minuscule, dont la solution se vérifie à la main.

    La section 10.5 du plan pose comme critère de fin du solveur qu'il « tourne
    sur un petit cas de test où la solution est connue ou vérifiable à la main,
    avant d'être utilisé sur le cas complet ».

    Cas proposé : un réservoir, deux quartiers, deux conduites parallèles vers
    le même quartier de coûts c_1 et c_2. À l'optimum, le débit se répartit
    entre les deux conduites en proportion inverse des coûts — un résultat qui
    se pose en trois lignes et qui prend en défaut une erreur de signe ou de
    facteur.
    """
    pytest.skip("À construire par M1 et M5 une fois la topologie figée.")
