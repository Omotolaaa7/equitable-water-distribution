# Distribuer l'eau équitablement dans un quartier quand la demande est incertaine

**Thème 3 · Groupe 1**, Académie des Mathématiques Appliquées (AMA)
Superviseur : Ir. Charbel Mamlankou

---

## Le problème

Une société de distribution d'eau alimente plusieurs quartiers depuis quelques réservoirs,
via un réseau de conduites à débit limité. La répartition actuelle est empirique,
proportionnelle à la demande historique, et la demande de chaque quartier varie de façon
imprévisible d'un jour à l'autre.

**Objectif.** Produire un outil qui calcule une répartition de l'eau plus équitable et moins
coûteuse que la pratique actuelle, et qui reste fiable lorsque la demande réelle s'écarte
des prévisions.

**Formulation.** Sur le graphe du réseau `G = (V, E)` de matrice d'incidence `A` :

```
q* = argmin_q  Σ_{e∈E} c_e q_e²      sous      Aq = b ,   q ≥ 0
```

La contrainte d'égalité est traitée **par pénalisation** (jamais par multiplicateurs de
Lagrange, ce que la Contrainte méthodologique 2 du sujet interdit explicitement) :

```
J(q) = Σ_e c_e q_e² + µ ‖Aq − b‖²
∇J(q) = 2Cq + 2µ Aᵀ(Aq − b)      avec  C = diag(c_e)
```

et la contrainte de positivité `q ≥ 0` par **projection** `max(·, 0)` à chaque itération de
la descente de gradient.

**Livrable central.** Une comparaison chiffrée entre la distribution actuelle
(proportionnelle aux demandes) et la distribution optimisée `q*`, testée sur plusieurs
scénarios de demande simulés par Monte-Carlo.

---

## ⚠ Règle qui gouverne tout ce dépôt

> Le code ne précède jamais la théorie.

Toute formule implémentée ici (gradient, critère d'arrêt, borne sur le pas, métrique) doit
avoir été **entièrement dérivée à la main dans le rapport** avant d'être codée
(Contrainte méthodologique 1 du sujet).

Les modules de ce dépôt sont donc livrés à l'état de **squelettes documentés** : chaque
fonction porte son contrat, son responsable et la dérivation dont elle dépend, et lève
`NotImplementedError` tant que cette dérivation n'a pas été validée par le groupe.

Le **jalon de passage obligatoire** (section 16 du plan de projet) liste les huit points à
cocher avant d'écrire la première ligne de `src/optimization/` :

1. Graphe du réseau figé (nœuds, arêtes, capacités, orientations) et validé par le groupe
2. Matrice d'incidence `A` construite, rang et conditionnement étudiés
3. Modèle probabiliste de la demande validé (loi, `µ_i`, `σ_i`, justification)
4. Convexité de `J(q)` démontrée **par écrit**
5. `∇J(q)` dérivé à la main et relu par au moins deux membres autres que son auteur
6. Règle de mise à jour et projection écrites en pseudo-code
7. Conditions de convergence établies (borne `η < 2/L`, critère d'arrêt)
8. Stratégie de référence définie précisément

Le suivi de ces cases se tient dans [report/STRUCTURE_RAPPORT.md](report/STRUCTURE_RAPPORT.md).

---

## Arborescence

Reprise à l'identique de la section 7 du plan de projet, pour que personne ne réinvente sa
propre structure.

```
Projet2/
├─ data/
│  ├─ generate_network.py      # génère un réseau synthétique réaliste
│  └─ network_config.json      # V, E, capacités, coûts, mu_i, sigma_i
├─ notebooks/
│  └─ exploration.ipynb        # exploration libre, jamais un livrable
├─ src/
│  ├─ graph/
│  │  ├─ build_graph.py        # construit G et la matrice d'incidence A
│  │  └─ graph_analysis.py     # connexité, fragilité, rang, conditionnement
│  ├─ probability/
│  │  ├─ demand_model.py       # D_i ~ N(mu_i, sigma_i²), estimateurs, IC
│  │  └─ monte_carlo.py        # génération de scénarios, statistiques agrégées
│  ├─ optimization/
│  │  ├─ objective.py          # J(q) et grad_J(q)
│  │  └─ gradient_descent.py   # descente de gradient projetée
│  ├─ simulation/
│  │  └─ run_scenarios.py      # orchestration : résolution sur chaque scénario
│  └─ evaluation/
│     ├─ baseline.py           # distribution actuelle (proportionnelle)
│     ├─ metrics.py            # coût, équité, violation de contrainte
│     └─ compare_strategies.py
├─ experiments/                # les 6 expériences imposées (section 6 du plan)
├─ results/{figures,tables}/   # sorties régénérables, non versionnées
├─ report/                     # rapport final, aucun code source dedans
├─ tests/                      # garde-fous pytest
└─ docs/                       # sujet AMA + plan de projet du groupe
```

---

## Les 6 expériences imposées

| Script | Objet | Vérifie |
|---|---|---|
| `exp1_baseline_vs_optimal.py` | Référence vs `q*` sur la demande moyenne | Le livrable central |
| `exp2_monte_carlo_robustness.py` | Robustesse sur N scénarios | Loi des grands nombres |
| `exp3_sensitivity_mu.py` | Sensibilité au paramètre de pénalisation `µ` | Exigence (v) du sujet |
| `exp4_convergence_check.py` | Pas `η` sous et au-delà de `2/L` | Théorie ↔ expérience (1) |
| `exp5_conditioning_vs_mesh.py` | Maillage du réseau vs `κ(A)` | Théorie ↔ expérience (2) |
| `exp6_at_risk_districts.py` | Quartiers à demande atypique | Volet statistique |

---

## Répartition (6 membres)

| Membre | Périmètre | Livrables vérifiables |
|---|---|---|
| **M1** | Modélisation du problème et réseau | `data/network_config.json`, schéma du graphe, section « Formulation du problème » |
| **M2** | Algèbre linéaire et structure discrète | `src/graph/graph_analysis.py`, preuves rang/conditionnement |
| **M3** | Probabilités et statistiques | `src/probability/demand_model.py`, estimateurs et IC |
| **M4** | Optimisation et dérivation du gradient | Dérivations manuscrites, pseudo-code, conditions de convergence |
| **M5** | Monte-Carlo, implémentation, expérimentation | `src/optimization/`, `monte_carlo.py`, les 6 expériences |
| **M6** | Validation, comparaison, intégration, rédaction | `src/evaluation/`, rapport complet, checklist |

Chaîne de dépendances : **M1 → M2 → M4 → M5 → M6**, avec **M3 → M5** en parallèle.
Personne ne code une formule avant que son auteur théorique ne l'ait fait relire.

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

```bash
python data/generate_network.py --config data/network_config.json
python experiments/exp1_baseline_vs_optimal.py
pytest
```

Les scripts s'exécutent depuis la racine du dépôt : ils ajoutent `src/` au chemin
d'import eux-mêmes.

---

## Documents de référence

- [docs/sujets_ama.pdf](docs/sujets_ama.pdf) : l'énoncé officiel des quatre thèmes
- [docs/plan_projet_theme3_groupe1.pdf](docs/plan_projet_theme3_groupe1.pdf) : le plan de projet du groupe
- [CONTRIBUTING.md](CONTRIBUTING.md) : conventions de travail à 6 sur le dépôt
