# Ce qui existe déjà, expliqué simplement

État du projet au 31 août 2026, après la fusion des branches, le branchement du modèle de
demande sur le fichier de configuration et la réparation de l Expérience 6. Toutes les valeurs de ce document
ont été produites en exécutant le code du dépôt, pas recopiées d'ailleurs.

À lire juste après [01_le_projet_sans_maths.md](01_le_projet_sans_maths.md). Le document 01
raconte ce que le projet veut faire, celui-ci montre ce qui est construit.

---

## 1. Ce que le projet fabrique

Un outil qui répond à une question : par quels tuyaux faire passer l'eau, et en quelle quantité,
pour que les huit quartiers soient servis au moindre coût.

Tout le reste sert à répondre à cette question proprement, et à pouvoir défendre la réponse.

## 2. La carte du dépôt

Où trouver quoi, quand on ouvre le projet pour la première fois.

| Dossier | Ce qu'il contient |
|---|---|
| `data/` | La description du réseau et le code qui la lit |
| `src/graph/` | Le graphe et la matrice `A` |
| `src/probability/` | Le modèle de demande et les tirages au hasard |
| `src/optimization/` | Le calcul de la meilleure répartition. Encore vide |
| `src/simulation/` | L'enchaînement des calculs sur chaque scénario. Encore vide |
| `src/evaluation/` | La comparaison avec la méthode actuelle. Encore vide |
| `experiments/` | Les six expériences imposées par le sujet |
| `results/` | Les figures et tableaux produits |
| `report/` | Le rapport final, sans une ligne de code dedans |
| `docs/` | Le sujet, le plan de projet, et les sections de rapport déjà rédigées |
| `tests/` | Les vérifications automatiques du code |

## 3. Ce qu'a fait ATTIOU19, le Membre 1

### La topologie

Il a **figé la topologie** (la liste de qui est relié à qui). Concrètement, il a rempli le
fichier `data/network_config.json` avec 2 réservoirs, 8 quartiers et 13 conduites, en précisant
pour chaque conduite son débit maximal et son coût unitaire.

Le mot « figé » compte. Tant que ce fichier bouge, personne d'autre ne peut travailler
sérieusement, parce que tous les calculs en dépendent.

### Les hypothèses

Il a aussi écrit ses **hypothèses de modélisation** (les choix qu'on assume faute de certitude),
ce qui pèse autant que les chiffres dans la notation.

L'offre totale vaut 360 m³/h pour une demande moyenne de 300 m³/h, soit 20 % de marge. Ce choix
est délibéré : sans marge, les journées de forte consommation rendraient le problème impossible
à résoudre.

Il a également décidé que Q1 serait le seul quartier desservi par une seule conduite, pour avoir
un point de fragilité à étudier.

### Le chargement et la validation

Il a codé `data/generate_network.py`, 372 lignes, qui lit le fichier et vérifie qu'il tient
debout. Cette vérification refuse par exemple un coût négatif ou nul.

Ce refus n'est pas de la coquetterie. Un coût strictement positif est l'hypothèse exacte dont
dépend une démonstration mathématique plus loin dans le projet, celle de la convexité. Un coût
nul casserait la démonstration sans provoquer la moindre erreur visible.

## 4. Ce qu'a fait Godwin Akakpo, le Membre 2

### La traduction du dessin en nombres

Un ordinateur ne sait pas manipuler un dessin de réseau. Godwin a donc traduit le dessin en
tableau de nombres. Ce tableau s'appelle la **matrice d'incidence** (le réseau écrit en
chiffres), notée `A`.

La voici, celle de votre projet, telle que le code la produit :

```
           1    2    3    4    5    6    7    8    9   10   11   12   13
          R1   R1   Q2   Q3   R2   R2   Q6   Q7   Q4   Q3   Q2   Q5   Q6
          Q1   Q2   Q3   Q4   Q5   Q6   Q7   Q8   Q5   Q6   Q4   Q6   Q8
       -----------------------------------------------------------------
    R1 |   -1   -1    .    .    .    .    .    .    .    .    .    .    .
    R2 |    .    .    .    .   -1   -1    .    .    .    .    .    .    .
    Q1 |    1    .    .    .    .    .    .    .    .    .    .    .    .
    Q2 |    .    1   -1    .    .    .    .    .    .    .   -1    .    .
    Q3 |    .    .    1   -1    .    .    .    .    .   -1    .    .    .
    Q4 |    .    .    .    1    .    .    .    .   -1    .    1    .    .
    Q5 |    .    .    .    .    1    .    .    .    1    .    .   -1    .
    Q6 |    .    .    .    .    .    1   -1    .    .    1    .    1   -1
    Q7 |    .    .    .    .    .    .    1   -1    .    .    .    .    .
    Q8 |    .    .    .    .    .    .    .    1    .    .    .    .    1
```

Comment la lire. Chaque colonne est une conduite, chaque ligne est un point du réseau. Un `-1`
signale que la conduite part de là, un `+1` qu'elle y arrive, un point qu'elle ne touche pas ce
nœud.

Regardez la colonne 1. Elle contient un `-1` sur la ligne R1 et un `+1` sur la ligne Q1. Cette
conduite part du réservoir R1 et arrive au quartier Q1.

Regardez maintenant la ligne Q1. Elle contient un seul chiffre sur treize. Q1 n'a qu'une seule
conduite, et c'est le quartier fragile du réseau. On le voit d'un coup d'œil sur le tableau.

### Le vecteur b

À côté de la matrice, il y a une liste qui dit ce que chaque point apporte ou consomme, notée
`b`. Sur une journée moyenne :

```
    R1 :  -150.0   (injecte 150 m3/h)
    R2 :  -150.0   (injecte 150 m3/h)
    Q1 :   +25.0   (consomme 25 m3/h)
    Q2 :   +40.0   (consomme 40 m3/h)
    Q3 :   +35.0   (consomme 35 m3/h)
    Q4 :   +45.0   (consomme 45 m3/h)
    Q5 :   +40.0   (consomme 40 m3/h)
    Q6 :   +50.0   (consomme 50 m3/h)
    Q7 :   +30.0   (consomme 30 m3/h)
    Q8 :   +35.0   (consomme 35 m3/h)
```

Les réservoirs portent un signe négatif parce qu'ils donnent de l'eau. Les quartiers portent un
signe positif parce qu'ils en prennent. La somme vaut exactement zéro, ce qui est le contrôle
le plus simple que rien n'a été perdu en route.

### L'équation qui résume tout

Avec ces deux objets, on écrit `Aq = b`, où `q` est la liste des 13 débits qu'on cherche.

En français, cette équation dit : à chaque point du réseau, ce qui rentre moins ce qui sort
égale ce qui est consommé sur place. Rien de plus mystérieux que ça.

### Les quatre mesures

Godwin a aussi calculé quatre grandeurs sur cette matrice.

Le **rang** (le nombre de lignes qui apportent une information nouvelle) vaut 9, alors que la
matrice a 10 lignes. Une ligne est donc déductible des autres, et c'est normal : chaque conduite
prend de l'eau quelque part et la dépose ailleurs, donc le bilan global est toujours nul.

Le **noyau** (les répartitions qui ne changent rien pour personne) est de dimension 4. C'est le
point central du projet, développé en section 5.

Le **conditionnement** (la fragilité du calcul face aux erreurs d'arrondi) vaut 4,724. Une
petite valeur, donc votre réseau se calcule sans difficulté. Godwin a évité un piège ici : la
formule habituelle aurait renvoyé l'infini sur ce type de matrice, et il a utilisé la bonne
variante.

La **constante de Lipschitz** (la raideur maximale du problème), qui servira au Membre 4 pour
choisir la taille des pas de calcul.

### Sa section de rapport

Il a rédigé 619 lignes de LaTeX (langage de mise en page pour les formules), compilées en PDF,
avec les démonstrations du rang, du noyau, des points de fragilité et du conditionnement, plus
trois figures. C'est dans `docs/algebre_lineaire/`.

## 5. Le point le plus important du projet, et il est simple

Votre réseau contient des boucles. Pour aller de Q2 à Q4, il existe deux chemins : le long, en
passant par Q3, et le raccourci direct par la conduite 11.

J'ai testé sur votre vrai réseau ce que ça change. J'ai fait passer 1 m³/h de plus par le chemin
long, et 1 m³/h de moins par le raccourci :

```
  resultat A*z = [0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
  tout est a zero : personne ne recoit un litre de plus ou de moins.
```

Dix zéros, un par point du réseau. Personne ne voit la différence. Les deux répartitions
satisfont également tout le monde.

Il existe donc plusieurs façons correctes de distribuer l'eau, et elles ne coûtent pas la même
chose. Votre réseau en compte exactement 4 indépendantes, ce qui est justement la dimension du
noyau calculée par Godwin.

Voilà le sujet du projet : choisir la moins chère parmi toutes les répartitions correctes.

Si vous ne retenez qu'une chose de ce document, retenez celle-là. C'est aussi la meilleure
réponse d'ouverture en soutenance.

## 6. Ce qu'a fait CLEMOU, le Membre 3

### Le modèle de demande

Il a modélisé le fait qu'on ne connaît jamais la demande à l'avance. Chaque quartier suit une
**loi normale** (la courbe en cloche), décrite par deux nombres : sa moyenne et sa dispersion.

Pour Q1 par exemple, la moyenne vaut 25 m³/h et la dispersion 5. Ce qui veut dire que deux jours
sur trois, Q1 consomme entre 20 et 30, et dix-neuf jours sur vingt entre 15 et 35.

### Les corrélations

Il a ajouté les **corrélations** (le fait que des quartiers voisins consomment plus en même
temps), parce qu'une canicule frappe tout un secteur d'un coup plutôt qu'un seul quartier.

Sans cette précaution, on sous-estimerait le risque. Quand les quartiers sont indépendants,
leurs écarts se compensent et le total reste stable. Quand ils sont corrélés, les écarts
s'additionnent.

### Les journées simulées

Concrètement, son code sait fabriquer des journées possibles. Cinq exemples tirés au hasard :

```
  quartier       Q1      Q2      Q3      Q4      Q5      Q6      Q7      Q8   TOTAL
  moyenne      25.0    40.0    35.0    45.0    40.0    50.0    30.0    35.0    300.0
  jour 1       23.8    37.5    37.9    38.2    37.1    50.6    20.1    31.7    276.9
  jour 2       15.4    42.4    34.6    52.8    42.5    49.8    36.9    32.5    306.8
  jour 3       23.9    39.4    39.4    57.3    45.0    50.3    37.2    43.8    336.4
  jour 4       23.5    40.3    28.7    50.7    47.0    55.8    27.7    32.3    306.1
  jour 5       15.2    41.3    31.1    40.7    33.6    55.0    38.2    39.9    295.0
```

Regardez la colonne TOTAL. Aucune journée ne ressemble à la moyenne de 300. Sur cinq tirages
seulement, le total oscille entre 277 et 336.

C'est exactement la difficulté du sujet. Un plan calé sur la moyenne serait calé sur une journée
qui ne se produit presque jamais.

Cette façon de faire, tirer beaucoup de journées au hasard et regarder ce qui sort, s'appelle
**Monte-Carlo** (simuler des milliers de scénarios). Le plan en prévoit 1000.

### Le reste de son travail

Il a aussi calculé les **intervalles de confiance** (une fourchette qui encadre une valeur
estimée), identifié les quartiers qui consomment souvent autrement que prévu, et produit quatre
figures dans `results/figures/`. Sa section de rapport est dans
`docs/probabilites_statistiques/`.

## 7. Ce qui manque encore, et qui est votre partie

Aujourd'hui, on sait décrire le réseau, écrire l'équation `Aq = b`, et fabriquer des journées
possibles. Personne ne sait encore **choisir** la meilleure répartition parmi les quatre degrés
de liberté.

Il manque trois briques, et elles s'enchaînent.

La **fonction de coût**, qui dit combien coûte une répartition donnée. Elle est en carré :
doubler un débit multiplie son coût par quatre. Cette forme pousse à étaler les débits plutôt
qu'à les concentrer, et c'est de là que viendra le gain sur la méthode actuelle.

La **pénalisation** (remplacer une règle obligatoire par une amende), qui permet de traiter
l'équation `Aq = b` avec la seule méthode vue en cours. Au lieu d'interdire de violer la
conservation, on la rend coûteuse.

La **descente de gradient** (avancer petit à petit dans le sens de la pente), qui cherche le
fond de la vallée. Avec une **projection** (ramener dans le domaine autorisé) à chaque pas, pour
interdire les débits négatifs, qui n'auraient aucun sens physique.

Ces trois briques sont bloquées tant que le Membre 4 n'a pas écrit et fait relire ses
démonstrations. C'est le jalon du plan de projet, et il est noté.

## 8. Où en est chaque fichier

| Fichier | Lignes | État |
|---|---|---|
| `data/generate_network.py` | 372 | Fait par M1 |
| `src/graph/build_graph.py` | 226 | Fait par M2 |
| `src/graph/graph_analysis.py` | 260 | Fait par M2 |
| `src/probability/demand_model.py` | 358 | Fait par M3, lit la configuration, 7 tests passent |
| `src/probability/monte_carlo.py` | 92 | 4 fonctions vides, à faire par M5 |
| `src/optimization/objective.py` | 149 | 6 fonctions vides, bloquées par le jalon |
| `src/optimization/gradient_descent.py` | 135 | 3 fonctions vides, bloquées par le jalon |
| `src/simulation/run_scenarios.py` | 79 | 3 fonctions vides, à faire par M5 |
| `src/evaluation/baseline.py` | 50 | 1 fonction vide, à faire par M6 |
| `src/evaluation/metrics.py` | 97 | 6 fonctions vides, à faire par M6 |
| `src/evaluation/compare_strategies.py` | 75 | 4 fonctions vides, à faire par M6 |

Une fonction « vide » contient sa description complète et son contrat, mais pas encore son
calcul. Elle lève une erreur si on l'appelle. C'est voulu, pour éviter qu'un résultat faux passe
inaperçu.

### Où en est chaque membre, au 31 août 2026

| Membre | Sa partie | État |
|---|---|---|
| M1, ATTIOU19 | Réseau et hypothèses | Livré. Configuration, code de chargement, 3 documents Word |
| M2, Godwin Akakpo | Algèbre linéaire | Livré. Code complet et section de rapport compilée |
| M3, CLEMOU | Probabilités et statistiques | Livré. Code complet, section de rapport, 4 figures |
| **M4** | **Optimisation** | **Rien livré à ce jour.** Aucun commit, aucune section de rapport |
| **M5** | **Code et expériences** | **1 expérience sur 6.** Les 4 modules restent vides |
| M6 | Comparaison et rapport | Ne peut pas commencer tant que M5 n'a pas de résultats |

### Les six expériences, une par une

| Expérience | État | Qui |
|---|---|---|
| 1, référence contre `q*` | Non écrite | M5, bloquée par le jalon |
| 2, robustesse Monte-Carlo | Non écrite | M5, bloquée par le jalon |
| 3, sensibilité à `µ` | Non écrite | M5, bloquée par le jalon |
| 4, borne de convergence | Non écrite | M5, bloquée par le jalon |
| 5, maillage et conditionnement | Non écrite | M5, bloquée par le jalon |
| 6, quartiers à risque | Faite et exécutable | M3 |

L'Expérience 1 est le livrable central que le sujet réclame explicitement, la comparaison
chiffrée entre la distribution actuelle et `q*`. Elle n'existe pas encore.

Le dossier `results/tables/` est vide. Les quatre figures présentes viennent toutes de
l'Expérience 6.

### Ce qui bloque, en une phrase

Le Membre 4 doit écrire ses démonstrations et les faire relire par deux personnes. Tant que ce
jalon n'est pas franchi, le solveur ne peut pas être codé, les cinq expériences ne peuvent pas
tourner, et le Membre 6 n'a rien à analyser.

### Les corrections faites les 30 et 31 août

Trois problèmes ont été trouvés en relisant le code fusionné, et réglés.

Les corrélations entre quartiers différaient sur 15 paires sur 28 entre le fichier du Membre 1
et le code du Membre 3. Le code cherchait des cases nommées en anglais dans un fichier nommé en
français, et retombait en silence sur des valeurs écrites en dur. Le code lit maintenant les
bons noms, et sept tests le vérifient paire par paire.

L'Expérience 6 plantait au lancement, un bout de squelette étant resté en tête de fichier. Elle
s'exécute maintenant de bout en bout.

La figure des matrices de corrélation affichait encore les anciennes valeurs. Les quatre figures
ont été régénérées.

## 9. Refaire ces calculs vous-même

Toutes les valeurs de ce document se reproduisent en cinq minutes. Depuis la racine du dépôt,
avec l'environnement installé :

```bash
python -c "import sys; sys.path.insert(0,'.'); from data.generate_network import charger_reseau, valider_reseau; from src.graph.build_graph import construire_matrice_incidence; from src.graph import graph_analysis as ga; r=charger_reseau('data/network_config.json'); A=construire_matrice_incidence(r); print('anomalies :', valider_reseau(r) or 'aucune'); print('A', A.shape, 'rang', ga.rang(A), 'noyau', ga.noyau(A).shape[1], 'cond', round(ga.conditionnement(A),3))"
```

Le faire soi-même une fois vaut mieux que de me croire sur parole. Et si un jour les chiffres de
ce document ne correspondent plus, c'est que quelqu'un a modifié la topologie.

## 10. Les mots qu'on entend en réunion

Ceux qui reviennent le plus souvent, avec leur traduction en langage courant.

| Le mot | Ce que ça veut dire, simplement |
|---|---|
| Topologie | Qui est relié à qui dans le réseau |
| Graphe | Un dessin de points reliés par des traits |
| Nœud | Un point du réseau, réservoir ou quartier |
| Arête, ou conduite | Un tuyau entre deux points |
| Matrice | Un tableau de nombres |
| Matrice d'incidence | Le réseau écrit sous forme de tableau |
| Conservation des flux | Ce qui rentre égale ce qui sort plus ce qui est consommé |
| Rang | Le nombre de lignes qui apportent une information nouvelle |
| Noyau | Les répartitions qui ne changent rien pour personne |
| Conditionnement | À quel point le calcul est fragile aux arrondis |
| Loi normale | La courbe en cloche |
| Écart-type | De combien les valeurs s'écartent de la moyenne |
| Corrélation | Le fait que deux quartiers bougent ensemble |
| Monte-Carlo | Simuler des milliers de journées au hasard |
| Intervalle de confiance | Une fourchette qui encadre une valeur estimée |
| Fonction de coût | Ce qu'on cherche à rendre le plus petit possible |
| Gradient | La direction de la pente la plus raide |
| Descente de gradient | Avancer petit à petit dans le sens de la pente |
| Convexité | La forme de bol, avec un seul fond |
| Pénalisation | Remplacer une règle obligatoire par une amende |
| Projection | Ramener une valeur dans le domaine autorisé |
| Solveur | Le programme qui trouve la meilleure répartition |

Le glossaire complet, avec les symboles mathématiques, est dans
[07_glossaire.md](07_glossaire.md).

## 11. Deux problèmes réglés

### Les corrélations, réglé le 31 août 2026

Pendant plusieurs jours, le fichier du Membre 1 et le code du Membre 3 ne disaient pas la même
chose sur la façon dont les quartiers consomment ensemble. Le fichier annonçait 0,30 sur neuf
paires, le code utilisait 0,40 entre voisins directs et 0,15 à deux conduites. Sur 28 paires,
15 divergeaient.

La cause était bête et instructive. Le code cherchait des cases nommées en anglais,
`districts` et `correlations`, alors que le fichier les nomme en français, `noeuds` et
`correlations_voisinage`. Aucun nom ne correspondait, et le code retombait en silence sur des
valeurs écrites en dur.

Le code lit maintenant les bons noms, et une structure inconnue lève une erreur explicite au
lieu de se rabattre sans rien dire. Sept tests dans `tests/test_demand_model.py` comparent
paire par paire ce que le code charge et ce que le fichier déclare.

La règle du Membre 3 reste disponible sous le nom `paires_voisinage_depuis_topologie`, qui la
déduit du graphe. Elle produit les entrées à coller dans le fichier si le groupe la retient.

### L'expérience 6, réglée le 31 août 2026

Le script plantait au lancement. Le bout de squelette était resté en haut du fichier et levait
son erreur avant d'atteindre le vrai code, écrit en dessous. Les quatre figures existaient
quand même, elles avaient été produites en appelant la fonction à la main.

Le script tourne maintenant de bout en bout, et ses quatre figures ont été régénérées. Celle
des matrices de corrélation affichait encore 0,40 et 0,15, des valeurs qui ne sont plus celles
du modèle.

## 12. Ce qui vient ensuite, dans l'ordre

Le Membre 4 écrit sa preuve de convexité, dérive le gradient à la main, établit la borne sur le
pas d'apprentissage et le critère d'arrêt, puis fait relire le tout par deux autres membres.
C'est le jalon, et c'est aujourd'hui le seul obstacle réel.

Le Membre 5 code alors `objective.py` et `gradient_descent.py` d'après ces dérivations, vérifie
le gradient par différences finies, et valide le solveur sur le petit cas à deux conduites
parallèles dont la solution se pose à la main.

Le Membre 5 complète `monte_carlo.py` et `run_scenarios.py`, puis lance les Expériences 1, 4, 3,
2 et 5, dans cet ordre, et produit les figures et les tableaux.

Le Membre 6 code la stratégie de référence et les métriques, construit la comparaison chiffrée,
puis rédige et assemble le rapport.

Le rapport ne peut pas être finalisé avant que ces quatre étapes soient passées. Donner la main
au Membre 6 aujourd'hui reviendrait à lui demander d'analyser des résultats qui n'existent pas,
et de rédiger deux rubriques de la grille de notation qui pèsent 35 % à elles deux.
