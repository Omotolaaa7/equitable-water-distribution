# Rapport final — structure imposée et checklist de conformité

Responsable : **M6**, avec les contributions de tous.
Rubrique « Rédaction & rigueur » : 10 % de la note, mais ce document conditionne
aussi les 90 % restants, puisque c'est dans le rapport que sont évaluées les
démonstrations.

> **Aucun extrait de code source dans ce dossier.** Ni listing, ni capture
> d'écran de code. Le pseudo-code est accepté, et lui seul. C'est la Contrainte
> méthodologique 1 du sujet, et elle est vérifiée.

---

## Les 9 sections imposées

| # | Section | Contenu attendu | Porteur |
|---|---|---|---|
| 1 | Introduction | Contexte, problématique, motivation, brève revue des approches existantes | M6 |
| 2 | Formulation du problème | Variables, paramètres, hypothèses, contraintes | M1 + M6 |
| 3 | Développement mathématique | Les **cinq volets** ci-dessous, ordre libre | M1–M4 |
| 4 | Méthode numérique | Passage explicite mathématiques → algorithme, **en pseudo-code uniquement** | M4 + M5 |
| 5 | Expériences numériques | Vérification empirique d'au moins **deux** résultats théoriques de la section 3 | M5 |
| 6 | Analyse des résultats | Interprétation **mathématique**, pas seulement descriptive | M6 + M3 |
| 7 | Limites et améliorations | | M6 |
| 8 | Conclusion | | M6 |
| 9 | Références bibliographiques | Toutes les sources utilisées | tous |

### Les cinq volets de la section 3

Aucun groupe ne peut se limiter à un sous-ensemble du cours. Les cinq doivent
apparaître, et chacun est noté séparément.

| Volet | Contenu pour le Thème 3 | Porteur | Poids |
|---|---|---|---|
| Représentation algébrique | Matrice d'incidence `A`, système `Aq = b`, rang, noyau, conditionnement, spectre de `2C + 2µAᵀA` | M2 | 15 % |
| Modélisation probabiliste | `D_i ~ N(µ_i, σ_i²)`, justification de la loi, covariance entre quartiers voisins | M3 | 20 % |
| Analyse statistique | Estimateurs de `µ_i` et `σ_i`, intervalles de confiance, test de significativité | M3 | *(idem)* |
| Formulation d'optimisation | `min_q J(q)`, convexité, dérivation **complète** de `∇J` | M4 | 20 % |
| Structure discrète | Graphe `G = (V,E)`, connexité, points de fragilité, cycles et noyau de `A` | M1 + M2 | 10 % |

---

## Les six éléments obligatoires (Contrainte méthodologique 3)

Indépendamment du plan retenu, le rapport doit contenir explicitement :

- [ ] **(i)** Une proposition mathématique justifiée — ici : convexité de `J`
- [ ] **(ii)** Une dérivation complète de `∇J(q) = 2Cq + 2µAᵀ(Aq − b)`
- [ ] **(iii)** Un algorithme correctement justifié — descente de gradient projetée
- [ ] **(iv)** Une validation numérique confrontant théorie et expérience — Expériences 4 et 5
- [ ] **(v)** Une analyse de sensibilité d'au moins un hyperparamètre — Expérience 3 sur `µ`
- [ ] **(vi)** Une comparaison à une stratégie de référence — Expérience 1, distribution proportionnelle

---

## Jalon de passage vers le code

Tant que ces huit cases ne sont pas cochées, **aucune ligne de `src/optimization/`
ne doit être écrite** (section 16 du plan).

- [ ] 1. Graphe du réseau figé (nœuds, arêtes, capacités, orientations), validé par le groupe — *M1*
- [ ] 2. Matrice `A` construite formellement, rang et conditionnement étudiés — *M2*
- [ ] 3. Modèle probabiliste validé (loi, `µ_i`, `σ_i`, justification) — *M3*
- [ ] 4. Convexité de `J(q)` démontrée **par écrit** — *M4*
- [ ] 5. `∇J(q)` dérivé à la main, relu par **deux membres autres que son auteur** — *M4*
- [ ] 6. Règle de mise à jour et projection écrites en pseudo-code — *M4*
- [ ] 7. Conditions de convergence établies (`η < 2/L`, critère d'arrêt) — *M4 + M2*
- [ ] 8. Stratégie de référence définie précisément — *M6*

---

## Checklist finale (section 13 du plan)

Chaque case doit être cochée par **une personne autre que celle qui a produit
l'élément**.

**Théorie et mathématiques**
- [ ] Interprétation physique de `Aq = b` rédigée et validée
- [ ] Rang et conditionnement de `A` calculés **et interprétés**
- [ ] Choix de la loi normale pour `D_i` justifié
- [ ] Estimateurs de `µ_i`, `σ_i` et intervalles de confiance établis
- [ ] Convexité de `J(q)` démontrée
- [ ] `∇J(q)` dérivé complètement et relu par au moins deux personnes
- [ ] Règle de mise à jour et projection écrites explicitement
- [ ] Conditions de convergence (pas, critère d'arrêt) établies théoriquement
- [ ] Influence de `µ` discutée théoriquement

**Données**
- [ ] Réseau synthétique construit et documenté
- [ ] Paramètres de demande (`µ_i`, `σ_i`) calibrés et justifiés
- [ ] Corrélations entre quartiers définies, si retenues

**Simulation et code**
- [ ] Graphe et matrice d'incidence codés et testés
- [ ] Générateur Monte-Carlo fonctionnel
- [ ] Solveur (gradient projeté) fonctionnel et validé sur un petit cas test
- [ ] Distribution de référence (proportionnelle) codée

**Validation**
- [ ] Au moins deux résultats théoriques vérifiés empiriquement
- [ ] Analyse de sensibilité d'au moins un hyperparamètre réalisée

**Expériences**
- [ ] Les 6 expériences exécutées
- [ ] Figures et tableaux produits pour chacune

**Comparaison**
- [ ] Comparaison chiffrée référence contre `q*` sur **plusieurs** scénarios

**Rapport**
- [ ] Structure conforme aux 9 sections
- [ ] **Aucun extrait de code source**
- [ ] Les cinq volets du développement mathématique présents

**Bibliographie**
- [ ] Toutes les sources référencées

**Présentation / démonstration**
- [ ] Support de présentation prêt
- [ ] Outil final exécutable de bout en bout, testé avant la démonstration

---

## Grille de notation

| Rubrique | Critère | Poids |
|---|---|---|
| Formulation du problème | Clarté des variables, hypothèses, contraintes | 10 % |
| Algèbre linéaire | Représentation matricielle, spectre, conditionnement | 15 % |
| Probabilités & statistiques | Modélisation, estimateurs, IC, tests | 20 % |
| Optimisation | Dérivation du gradient, convergence, expérimentation | 20 % |
| Mathématiques discrètes | Usage **réel** (non cosmétique) du graphe | 10 % |
| Implémentation & validation | Qualité du code livré, confrontation théorie/expérience | 15 % |
| Rédaction & rigueur | Structure, notations, discussion des limites | 10 % |

---

## Format

LaTeX est recommandé par la section 10.3 du plan : un rapport dense en formules
est plus simple à mettre en forme et à corriger. Si le groupe choisit LaTeX,
déposer ici `main.tex` et un dossier `sections/`. Le `.gitignore` du dépôt
exclut déjà les sorties de compilation LaTeX.
