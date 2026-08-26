# Les maths depuis zéro, partie 2 : probabilités, statistiques, Monte-Carlo

Couvre la rubrique « Probabilités & statistiques », 20 % de la note, à égalité avec
l'optimisation pour le poids le plus lourd. La partie Monte-Carlo relève directement du
Membre 5.

---

## 1. Pourquoi cette partie existe

Toute la partie algèbre suppose qu'on connaît `b`, donc la demande de chaque quartier. On ne
la connaît pas. Elle change tous les jours, et personne ne sait de combien à l'avance.

Deux façons de traiter ça. La mauvaise : prendre la moyenne et faire comme si. La bonne :
modéliser l'incertitude, la simuler, et mesurer à quel point la solution y résiste.

Le sujet impose la bonne.

## 2. Une variable aléatoire

Une variable aléatoire, c'est une quantité dont la valeur change à chaque observation, et dont
on connaît la façon dont elle se répartit sans connaître la valeur précise du jour.

La demande du quartier Q1 en est une. Elle tourne autour de 120 m³/h, mais un mardi de mars
elle vaudra 108, et un samedi de canicule 151.

On la note `D_i` pour le quartier numéro `i`.

## 3. La loi normale

### 3.1 Ce que c'est

La loi normale, c'est la fameuse courbe en cloche. Elle décrit une quantité qui se concentre
autour d'une valeur centrale, avec des écarts de plus en plus rares à mesure qu'on s'éloigne.

On l'écrit :

```
D_i ~ N(µ_i , σ_i²)
```

Le symbole `~` se lit « suit la loi ». `µ_i` (mu) est la moyenne, le centre de la cloche.
`σ_i` (sigma) est l'écart-type, qui mesure la largeur de la cloche. Le carré `σ_i²` s'appelle
la variance.

### 3.2 Les trois repères à connaître par cœur

Pour une loi normale, quelle qu'elle soit :

68 % des valeurs tombent entre `µ − σ` et `µ + σ`.
95 % tombent entre `µ − 2σ` et `µ + 2σ`.
99,7 % tombent entre `µ − 3σ` et `µ + 3σ`.

Appliquons à Q1, qui a `µ = 120` et `σ = 18` dans notre configuration. Deux jours sur trois,
sa demande est entre 102 et 138. Dix-neuf jours sur vingt, elle est entre 84 et 156. Sortir de
l'intervalle 66 à 174 arrive trois fois sur mille.

Ces chiffres rendent le modèle concret, et un jury apprécie qu'on sache les sortir.

### 3.3 Pourquoi la loi normale, et pas une autre

Le sujet l'impose. Mais l'imposer ne dispense pas de la justifier, et la section 14 du plan
liste explicitement l'oubli de cette justification parmi les erreurs à éviter.

L'argument s'appelle le théorème central limite. Il dit ceci : quand on additionne un grand
nombre de petites quantités indépendantes, la somme se met à ressembler à une loi normale,
quelle que soit la forme de chaque petite quantité prise séparément.

Or la demande d'un quartier est exactement une somme de ce type. Des centaines de foyers qui
ouvrent leur robinet chacun de leur côté, sans se concerter, chacun pesant peu dans le total.

Le mot important est « indépendantes ». Un jour de match ou de coupure générale, les foyers ne
sont plus indépendants, ils agissent ensemble, et le théorème ne s'applique plus. C'est une
limite honnête à mentionner.

### 3.4 La faiblesse du modèle, à ne pas cacher

Une loi normale s'étend de moins l'infini à plus l'infini. Elle autorise donc mathématiquement
une demande négative, ce qui n'a aucun sens physique.

Avec nos écarts-types, entre 12 % et 28 % de la moyenne, il faudrait descendre à plus de trois
écarts-types sous la moyenne pour atteindre zéro. La probabilité est négligeable, mais le
rapport doit la chiffrer plutôt que de l'affirmer, et dire ce que le code fait si un tirage
négatif survient malgré tout.

Le Thème 4 du même énoncé impose d'ailleurs une loi tronquée ou log-normale pour cette raison
précise. Savoir que le voisin a ce problème et comment il le règle donne du relief à la
discussion.

## 4. Covariance et corrélation

### 4.1 L'idée

Deux quartiers voisins ne consomment pas indépendamment. La même vague de chaleur les frappe
tous les deux. Quand l'un consomme plus, l'autre aussi, en général.

La corrélation, notée `ρ` (rho), mesure ça. Elle vaut entre `−1` et `+1`.

`ρ = 0` : aucun lien.
`ρ = 0,4` : quand l'un monte, l'autre a tendance à monter aussi.
`ρ = −1` : quand l'un monte, l'autre descend systématiquement.

Notre configuration déclare `ρ = 0,40` entre Q1, Q2 et Q3, `ρ = 0,35` entre Q5, Q6 et Q7, et
`ρ = 0,30` entre Q9 et Q10.

### 4.2 La covariance et sa matrice

La covariance est la même idée, mais non normalisée. Elle se relie à la corrélation par :

```
Σ_ij = ρ_ij × σ_i × σ_j
```

On range toutes ces valeurs dans un tableau carré de 10 lignes et 10 colonnes, la matrice de
covariance, notée `Σ` (sigma majuscule, à ne pas confondre avec le Σ de la somme). Sur la
diagonale, on trouve les variances `σ_i²`, puisque `ρ_ii = 1`.

### 4.3 Le piège que M3 doit connaître

Une matrice de corrélation assemblée à la main, par blocs, n'est pas automatiquement valide.
Pour correspondre à une vraie loi gaussienne, elle doit être semi-définie positive (toutes ses
valeurs propres positives ou nulles).

Si elle ne l'est pas, elle ne décrit aucune loi réelle, et la génération des tirages échouera
au moment de la factorisation. Il faut vérifier le signe des valeurs propres et le signaler
franchement, plutôt que de corriger en silence.

### 4.4 Pourquoi la corrélation change le résultat

C'est le point que beaucoup ratent. Si les quartiers étaient indépendants, leurs écarts se
compenseraient : certains au-dessus, d'autres en dessous, et la demande totale resterait
proche de sa moyenne.

Avec une corrélation positive, les écarts s'additionnent au lieu de se compenser. La demande
totale devient beaucoup plus variable. Et c'est précisément cette variabilité totale qui met
le réseau en difficulté.

Ignorer la corrélation reviendrait donc à sous-estimer le risque.

## 5. Estimer : la statistique

On a 1000 tirages. Qu'est-ce qu'on en déduit.

### 5.1 Estimateur et biais

Un estimateur, c'est une recette qui part des données observées et produit une valeur approchée
d'une quantité qu'on ne connaît pas.

Un estimateur est dit sans biais si, en moyenne sur un très grand nombre de répétitions, il
tombe juste. Il peut se tromper à chaque fois, mais ses erreurs se compensent.

### 5.2 La moyenne empirique

La recette la plus simple : on additionne et on divise par le nombre.

```
µ̂_i = (1/n) × Σ_k D_i^(k)
```

Le petit chapeau sur `µ̂` signale une valeur estimée à partir des données, par opposition à la
vraie valeur `µ` qu'on ne connaîtra jamais. Cette notation revient partout, autant l'adopter
tout de suite.

Cet estimateur est sans biais.

### 5.3 La variance empirique, et le piège du `n − 1`

```
σ̂_i² = (1/(n−1)) × Σ_k (D_i^(k) − µ̂_i)²
```

Pourquoi diviser par `n − 1` et non par `n`. Parce qu'on a déjà utilisé les données une
première fois pour calculer `µ̂`. Les écarts sont donc mesurés par rapport à un centre qui a
été calé sur ces mêmes données, ce qui les rend systématiquement un peu trop petits. Diviser
par `n − 1` compense exactement ce rétrécissement. On appelle ça la correction de Bessel.

Le piège pratique : NumPy divise par `n` par défaut. Il faut passer `ddof=1` explicitement.

```python
np.var(echantillon, axis=0, ddof=1)
```

Oublier ce `ddof=1` ne fait rien planter. Ça biaise la variance, donc les intervalles de
confiance, donc l'Expérience 6. Sur 1000 tirages l'écart est infime, mais il est faux, et un
correcteur qui lit le code le verra.

### 5.4 L'intervalle de confiance

Un intervalle de confiance à 95 %, c'est une fourchette calculée à partir des données, construite
de telle sorte que si on répétait toute l'expérience un grand nombre de fois, 95 % des
fourchettes ainsi construites contiendraient la vraie valeur.

Formulation à surveiller. On dit souvent « il y a 95 % de chances que µ soit dans l'intervalle ».
Cette formulation est fausse au sens strict, parce que `µ` désigne une valeur fixe. C'est
l'intervalle qui bouge d'un échantillon à l'autre. La nuance revient souvent en soutenance.

La formule :

```
IC = [ µ̂_i ± t_{n−1, 1−α/2} × σ̂_i / √n ]
```

### 5.5 Pourquoi Student et pas la loi normale

Si on connaissait la vraie valeur de `σ`, on utiliserait les quantiles de la loi normale, et le
coefficient vaudrait 1,96 pour 95 %.

Mais on ne connaît pas `σ`, on l'estime lui aussi. Cette estimation ajoute de l'incertitude, et
la bonne loi devient celle de Student à `n − 1` degrés de liberté, dont les quantiles sont un
peu plus larges.

Sur 1000 tirages, l'écart entre Student et la loi normale est négligeable en valeur. Ce qui est
noté, c'est de savoir pourquoi on choisit l'un plutôt que l'autre.

### 5.6 Le test d'hypothèse

À la fin, on veut dire si la répartition optimisée coûte vraiment moins cher, ou si l'écart
observé pourrait venir du hasard de la simulation.

Le point de méthode important : les deux stratégies sont évaluées **sur les mêmes 1000
scénarios**. Les échantillons sont donc appariés (chaque valeur d'un côté a sa jumelle de
l'autre). Il faut un test apparié, qui compare les différences deux à deux.

Utiliser un test à deux échantillons indépendants ici serait une erreur de méthode, pas
seulement un choix moins bon. Le test apparié est plus puissant parce qu'il élimine la
variabilité commune aux deux stratégies, celle qui vient du scénario lui-même.

La p-valeur qui sort du test se lit ainsi : c'est la probabilité d'observer un écart au moins
aussi grand que celui mesuré, si en réalité les deux stratégies se valaient. Une p-valeur de
0,001 veut dire que cet écart serait très surprenant sous l'hypothèse d'égalité.

Une p-valeur ne dit pas que l'écart est important. Elle dit qu'il est difficilement attribuable
au hasard. Sur 1000 tirages, un écart minuscule peut sortir très significatif. Il faut donc
donner aussi la taille de l'effet, c'est-à-dire l'écart en pourcentage de coût.

## 6. Monte-Carlo, votre partie

### 6.1 Le principe

On ne sait pas calculer directement ce que donnera la répartition sur toutes les journées
possibles. Alors on en simule beaucoup, on calcule le résultat pour chacune, et on regarde la
distribution des résultats.

C'est tout. Le nom vient du casino de Monte-Carlo, à cause du hasard.

### 6.2 Comment on tire des demandes corrélées

Tirer 10 demandes indépendantes serait facile. Les tirer avec la bonne corrélation demande une
étape de plus.

La recette : on décompose la matrice de covariance `Σ` en un produit `Σ = L Lᵀ`, où `L` est
triangulaire. Cette décomposition s'appelle la factorisation de Cholesky. Ensuite, on tire un
vecteur `z` de 10 nombres indépendants suivant une loi normale centrée réduite, et on calcule :

```
D = µ + L z
```

Le résultat suit exactement la loi voulue, avec les bonnes moyennes, les bons écarts-types et
les bonnes corrélations.

En pratique, `numpy.random.Generator.multivariate_normal` fait tout ça. Savoir ce qu'il y a
dessous, c'est ce qui permet de comprendre pourquoi il plante quand `Σ` n'est pas semi-définie
positive.

### 6.3 La graine aléatoire

Un point de méthode qui vaut des points, et qui coûte cher si on l'oublie.

Il faut passer un générateur explicite avec une graine fixée :

```python
generateur = np.random.default_rng(42)
```

Sans graine fixée, deux exécutions donnent deux résultats différents. Les chiffres du rapport
ne seraient alors reproductibles par personne, et un correcteur qui relance le code
n'obtiendrait pas les valeurs citées. La configuration du projet fixe la graine à 42.

Éviter les appels directs à `np.random.normal`, qui utilisent un état global partagé. Le
générateur explicite rend le code testable et le résultat reproductible.

### 6.4 La loi des grands nombres

Plus on fait de tirages, plus la moyenne calculée se rapproche de la vraie moyenne. C'est
intuitif, et c'est un théorème.

Ce qui est moins intuitif, c'est la vitesse.

### 6.5 L'erreur en 1 sur racine de N, le résultat central de votre partie

L'incertitude sur une moyenne estimée à partir de `N` tirages vaut :

```
erreur standard = σ̂ / √N
```

La conséquence est frappante et vaut la peine d'être dite telle quelle en soutenance :
**pour diviser l'erreur par deux, il faut quatre fois plus de tirages.**

Chiffrons sur nos trois échelles.

| Nombre de tirages | `√N` | Erreur relative à `σ̂` |
|---|---|---|
| 100 | 10 | `σ̂ / 10` |
| 1 000 | 31,6 | `σ̂ / 31,6` |
| 10 000 | 100 | `σ̂ / 100` |

Passer de 100 à 10 000 tirages, donc multiplier le temps de calcul par 100, ne divise l'erreur
que par 10.

C'est ce qui justifie le choix de 1000 tirages comme valeur de référence. Et c'est aussi ce qui
explique pourquoi la section 14 du plan interdit de réduire `N` en silence pour gagner du temps :
la fiabilité statistique s'effondre plus vite qu'on ne le croit.

### 6.6 Ce que fait concrètement l'Expérience 2

On tire 1000 scénarios. Pour chacun, on résout le problème d'optimisation et on calcule aussi
la stratégie de référence. On obtient donc 1000 coûts optimisés et 1000 coûts de référence.

Ensuite on regarde, pour chaque groupe : la moyenne, la variance, les quantiles, et la
proportion de scénarios où la contrainte est bien respectée.

L'histogramme des deux distributions superposées est la figure la plus parlante du rapport,
parce qu'elle montre d'un coup d'œil non seulement qui coûte moins cher, mais aussi qui est
plus régulier.

Attention au temps de calcul. Mille scénarios multipliés par quelques milliers d'itérations de
descente, ça se compte en minutes, pas en secondes. Si ça devient bloquant, la solution est de
partir d'un point initial pertinent ou de resserrer la tolérance, jamais de baisser `N`.

### 6.7 L'Expérience 6, les quartiers à risque

On simule un historique de demande, en introduisant volontairement un biais sur certains
quartiers. Puis on regarde, pour chaque quartier, à quelle fréquence sa demande observée sort
de l'intervalle de confiance construit sur la demande prévue.

Le repère à garder en tête : un quartier bien modélisé sort de son intervalle à 95 % dans
environ 5 % des cas. C'est la définition même de l'intervalle. Un quartier qui en sort 30 % du
temps est atypique. Sans ce repère, le chiffre brut ne veut rien dire.

Le vrai intérêt de l'expérience est dans le croisement final. Un quartier à demande atypique
qui se trouve en plus en bout de réseau, relié par une seule conduite, cumule un risque
statistique et un risque structurel. C'est là que la partie probabilités et la partie graphe se
rejoignent, et ce genre de synthèse est ce qu'une grille de notation récompense.

Dans notre réseau, Q10 est le candidat évident.

---

## Ce qu'il faut savoir refaire au tableau

- Dessiner une courbe en cloche et placer `µ`, `µ ± σ`, `µ ± 2σ` avec les pourcentages.
- Donner l'intervalle à 95 % de Q1 de tête, à partir de `µ = 120` et `σ = 18`.
- Expliquer le théorème central limite avec les robinets du quartier, sans formule.
- Dire pourquoi `n − 1` et pas `n` dans la variance empirique.
- Dire pourquoi Student et pas la loi normale pour l'intervalle de confiance.
- Expliquer pourquoi il faut un test apparié et pas un test à deux échantillons.
- Dire ce que coûte le fait de diviser l'erreur Monte-Carlo par deux.
