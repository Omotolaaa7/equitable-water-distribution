# Le rôle du Membre 5, concrètement

Feuille de route opérationnelle. Que coder, dans quel ordre, ce qui bloque, et comment ne pas
attendre les autres pour rien.

---

## 1. Le périmètre, tel que le plan le définit

> **Mission.** Implémenter `monte_carlo.py`, coder `objective.py` et `gradient_descent.py` à
> partir des dérivations de Membre 4, exécuter toutes les expériences, produire les figures et
> tableaux.
>
> **Livrables vérifiables.** Code fonctionnel testé, résultats bruts de toutes les expériences,
> figures dans `results/figures`.
>
> **Dépendances.** Dépend de Membre 3 (modèle de demande) et de Membre 4 (dérivations validées).
> Alimente Membre 6.

C'est le poste avec la charge d'implémentation la plus lourde et la charge théorique la plus
légère. Le plan le dit explicitement en section 8.

Ce qui ne veut pas dire qu'on peut coder sans comprendre. Le code de M5 est la traduction
littérale des démonstrations de M4. Traduire sans comprendre, c'est ne pas voir passer une
erreur de signe.

## 2. La position dans la chaîne, et ce qu'elle implique

```
M1 (réseau)  →  M2 (matrice A, conditionnement)  →  M4 (convexité, gradient, borne sur le pas)
                                                              ↓
M3 (modèle de demande)  ────────────────────────────────→   M5  →  M6 (comparaison, rapport)
```

Le Membre 5 est en bout de chaîne côté théorie et en amont de tout côté résultats. Si M4 prend
trois jours de retard, M5 les prend aussi, et M6 après.

Deux conséquences pratiques.

La première, c'est qu'il faut réclamer. Pas attendre poliment que les dérivations arrivent.
Aller les chercher, poser des questions dessus, signaler dès qu'un délai devient un risque pour
la suite.

La seconde, c'est qu'il ne faut pas rester bloquée. Une bonne partie du travail de M5 ne dépend
ni de M3 ni de M4, et peut démarrer tout de suite.

## 3. Ce qui peut démarrer aujourd'hui, sans attendre personne

Le plan le prévoit d'ailleurs en Phase 1 : « M5 prépare l'environnement de code et
l'architecture des modules ».

**L'environnement.** Créer le venv, installer les dépendances, vérifier que `pytest` tourne.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
pytest
```

Les 8 tests doivent s'afficher comme ignorés, pas en erreur. S'ils sont en erreur, c'est un
problème d'installation à régler avant tout le reste.

**La compréhension du code existant.** Les squelettes de `src/` contiennent déjà, dans leurs
docstrings, le contrat de chaque fonction, son responsable et la formule qu'elle implémentera.
Les lire est le meilleur point d'entrée dans le projet.

**L'infrastructure d'expérience.** Les six scripts de `experiments/` ont tous la même forme :
charger la configuration, construire ce qu'il faut, boucler, tracer, sauver. Cette plomberie
peut s'écrire avant que le solveur existe. Un script qui tourne de bout en bout avec des
résultats bidons vaut mieux qu'un script parfait qui n'a jamais été lancé.

**Les fonctions de tracé.** Les figures des six expériences sont connues d'avance : un
diagramme en barres, un histogramme, des courbes de convergence superposées, un nuage de points,
un tableau. Rien de tout ça ne dépend du gradient.

**Les tests.** Écrire les tests avant le code testé est une bonne pratique, et ici c'est
possible : on sait déjà que la projection ne doit jamais renvoyer de négatif, qu'elle doit être
idempotente, que chaque colonne de A doit sommer à zéro. Les fichiers de `tests/` sont déjà là,
avec les intentions écrites.

## 4. Ce qui est bloqué, et par quoi exactement

| Ce que je veux coder | Bloqué par | Ce que j'attends précisément |
|---|---|---|
| `monte_carlo.generer_scenarios` | plus par M3 | Le modèle est livré, mais sous forme de classe. Voir la décision à prendre ci-dessous |
| `objective.objectif` | M4 | La formule de `J(q)` écrite et validée par le groupe |
| `objective.gradient` | M4 | La dérivation de `∇J` relue par deux membres |
| `gradient_descent.pas_maximal_theorique` | M4 et M2 | La borne `2/L` et la façon de calculer `L` |
| `gradient_descent.descente_projetee` | M4 | La règle de mise à jour et le critère d'arrêt en pseudo-code |
| Les 6 expériences | tout ce qui précède | Un solveur qui tourne sur un petit cas vérifiable |

Le jalon de la section 16 du plan est explicite : tant que les huit points ne sont pas cochés,
aucune ligne de code de `src/optimization/`.

Cette règle vient de la contrainte méthodologique 1 du sujet, elle est notée, et une pull
request qui implémente une formule doit pointer vers la section du rapport où elle est
démontrée.

### La décision à prendre sur le modèle de demande

Le Membre 3 a livré son travail, mais pas là où les expériences vont le chercher. Il a écrit
une classe `DemandModel` à la fin de `demand_model.py`, et les huit fonctions du squelette,
celles que `monte_carlo.py` et les six expériences appellent, lèvent toujours
`NotImplementedError`.

Deux façons de recoller, et le choix vous revient puisque c'est vous qui codez la suite.

**Brancher les fonctions sur la classe.** Chaque fonction du squelette devient une ou deux
lignes qui instancient `DemandModel` et appellent la méthode correspondante. Environ 30 lignes
en tout, rien d'autre ne bouge, les six expériences fonctionnent sans modification. C'est ce
que je ferais.

**Réécrire `monte_carlo.py` autour de la classe.** Plus propre sur le papier, mais il faut
alors reprendre les six scripts d'expérience, et le travail déjà fait par le Membre 3 dans
`exp6` devient un cas particulier à part.

Dans les deux cas, un problème reste à régler avec le Membre 1. La classe code en dur les
moyennes, les écarts-types et les corrélations, sans jamais lire `data/network_config.json`.
Les moyennes et les écarts-types concordent, les corrélations non : M1 déclare 0,3 sur 9 paires
précises, la classe utilise 0,40 entre voisins directs et 0,15 à deux conduites. Tant que ce
n'est pas tranché, le rapport et le code décrivent deux modèles différents.

Un troisième détail à corriger en passant : `experiments/exp6_at_risk_districts.py` ne
s'exécute pas en ligne de commande. Le `main()` du squelette est resté en tête de fichier et
lève son erreur avant que le code du Membre 3, collé en dessous, ne soit atteint.

## 5. L'ordre de travail recommandé

### Phase A, tout de suite

1. Monter l'environnement et vérifier que `pytest` tourne.
2. Lire les quatre documents de `docs/comprendre/`, dans l'ordre.
3. Lire tous les docstrings de `src/`, module par module.
4. Écrire `_bootstrap.py` et faire tourner un script d'expérience vide de bout en bout.
5. Écrire les fonctions de tracé avec des données inventées.

### Phase B, dès que M3 a figé le modèle de demande

6. `probability/demand_model.py` : extraction des paramètres, matrice de covariance,
   échantillonnage.
7. `probability/monte_carlo.py` : génération de scénarios, agrégation, erreur d'estimation.
8. Vérifier que les corrélations empiriques retrouvent celles déclarées dans la configuration.
   Un écart signale une erreur, et vaut mieux d'être vu maintenant que six expériences plus loin.

### Phase C, dès que M4 est relu et que le jalon est franchi

9. `optimization/objective.py` : `cout`, `violation_contrainte`, `objectif`, `gradient`,
   `hessienne`.
10. **`verifier_gradient` immédiatement après `gradient`, avant toute autre chose.** C'est le
    filet de sécurité qui rattrape les trois erreurs classiques.
11. `optimization/gradient_descent.py` : projection, borne sur le pas, boucle de descente.
12. Valider le solveur sur le petit cas à deux conduites parallèles, dont la solution se pose à
    la main. Le plan en fait un critère de fin de livrable.

### Phase D, une fois le solveur validé

13. `simulation/run_scenarios.py`.
14. Les six expériences, dans l'ordre 1, 4, 3, 2, 5, 6.

Pourquoi cet ordre plutôt que 1 à 6. L'Expérience 1 est le livrable central, elle passe en
premier. L'Expérience 4 vient ensuite parce qu'elle valide le solveur lui-même : si la
convergence ne se comporte pas comme la théorie l'annonce, tout ce qui suit est suspect. Puis
l'Expérience 3, qui fixe la bonne valeur de `µ` pour les autres. L'Expérience 2, la plus longue
à tourner, arrive quand les réglages sont stabilisés. Les 5 et 6 sont indépendantes du reste.

## 6. Le petit cas de test qui vaut de l'or

Le plan pose comme critère que le solveur « tourne sur un petit cas de test où la solution est
connue ou vérifiable à la main, avant d'être utilisé sur le cas complet ».

Voici ce cas, et il vaut la peine de le construire soi-même.

Un réservoir R, un quartier Q, deux conduites parallèles de R vers Q, de coûts `c₁` et `c₂`.
Le quartier demande `D`.

La conservation impose `q₁ + q₂ = D`. Le coût vaut `c₁q₁² + c₂q₂²`.

En remplaçant `q₂` par `D − q₁` et en dérivant, on trouve que l'optimum vérifie
`c₁q₁ = c₂q₂`. Autrement dit, **les débits se répartissent en proportion inverse des coûts.**

Avec `c₁ = 1`, `c₂ = 3` et `D = 100`, on attend `q₁ = 75` et `q₂ = 25`.

Ce cas prend en défaut une erreur de signe, un facteur 2 oublié et une transposée manquante, et
il tient en cinq lignes. Le construire avant de lancer quoi que ce soit sur le réseau à 13
conduites fait gagner des heures.

## 7. Les pièges d'implémentation qui coûtent cher

**Le `ddof=1`.** `np.var` divise par `n` par défaut. Il faut `ddof=1` pour la variance
empirique corrigée. Rien ne plante, tout est légèrement faux.

**`eigvals` au lieu de `eigvalsh`.** Sur une matrice symétrique, `eigvals` renvoie des valeurs
complexes avec des parties imaginaires numériques, et la comparaison au seuil `2/L` devient
bancale.

**L'ordre de calcul du gradient.** Écrire `A.T @ (A @ q - b)` et non `(A.T @ A) @ q - A.T @ b`.
La première forme fait deux produits matrice-vecteur. La seconde construit une matrice 13 × 13
à chaque appel, des milliers de fois dans la boucle.

**La graine aléatoire.** Passer un générateur explicite, `np.random.default_rng(42)`, jamais
`np.random.normal` directement. Sans ça, aucun chiffre du rapport n'est reproductible.

**La projection à chaque itération**, jamais une seule fois à la fin.

**L'overflow dans l'Expérience 4.** Au-delà de `2/L`, `J` explose en quelques dizaines
d'itérations. Prévoir une sortie propre plutôt qu'une sortie remplie de `inf`.

**Le temps de calcul de l'Expérience 2.** Mille scénarios multipliés par plusieurs milliers
d'itérations. Si ça devient bloquant, resserrer la tolérance ou partir d'un `q_initial`
pertinent, jamais baisser `N` en silence.

## 8. Ce que M6 attend de vous, et sous quelle forme

M6 construit la comparaison finale et rédige. Ce qui lui est utile :

des résultats bruts dans `results/tables/`, en CSV, une ligne par scénario, pas des chiffres
recopiés à la main dans un message ;

des figures dans `results/figures/`, avec des axes légendés et des unités, parce qu'une figure
sans unité ne peut pas entrer dans un rapport ;

et pour chaque expérience, la valeur des réglages utilisés, `µ`, `η`, la tolérance, le nombre
d'itérations, la graine. Sans ces valeurs, le résultat n'est pas reproductible et la figure
n'est pas défendable.

Le `.gitignore` du dépôt exclut `results/figures/` et `results/tables/` par défaut, puisque ces
fichiers se régénèrent. Au moment de la remise, les figures effectivement citées dans le rapport
doivent être ajoutées avec `git add -f`, sinon le rapport final renvoie à des fichiers absents
du dépôt.

## 9. Comment travailler sur le dépôt

Branche dédiée, jamais de push direct sur `main` :

```bash
git checkout -b m5-implementation
```

Commits en français, une ligne, qui disent ce que fait le commit et non quel fichier a été
touché. Pull request relue par au moins une autre personne. Les détails sont dans
[CONTRIBUTING.md](../../CONTRIBUTING.md).

Et pour toute pull request qui implémente une formule, mettre dans la description le renvoi vers
la section du rapport où elle est dérivée. Sans ce renvoi, elle n'est pas fusionnée.
