"""Amorce commune aux scripts d'expériences.

Les scripts de ``experiments/`` s'exécutent depuis la racine du dépôt. Cette
amorce ajoute la racine au chemin d'import pour que ``from src...`` fonctionne
sans installation ni variable d'environnement, et expose les chemins de sortie.

Importer ce module en premier, avant tout import de ``src`` :

    import _bootstrap  # noqa: F401
    from src.graph.build_graph import construire_matrice_incidence
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

CONFIG = RACINE / "data" / "network_config.json"
FIGURES = RACINE / "results" / "figures"
TABLEAUX = RACINE / "results" / "tables"

FIGURES.mkdir(parents=True, exist_ok=True)
TABLEAUX.mkdir(parents=True, exist_ok=True)
