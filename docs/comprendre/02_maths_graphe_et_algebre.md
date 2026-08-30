# Les maths depuis zéro, partie 1 : le graphe et l'algèbre

Couvre les rubriques « Mathématiques discrètes » (10 % de la note) et « Algèbre linéaire »
(15 %). Aucun prérequis au-delà du programme de terminale.

---

## 0. Savoir lire les symboles

Avant tout le reste. Un symbole non lu bloque une page entière.

| Symbole | Se lit | Veut dire |
|---|---|---|
| `Σ` | sigma | On additionne tout ce qui suit |
| `Σ_{e∈E}` | somme sur e appartenant à E | On additionne, une fois pour chaque conduite du réseau |
| `q` | q | La liste des débits, un par conduite |
| `q_e` | q indice e | Le débit sur la conduite qui s'appelle e |
| `A` | A | La matrice d'incidence, le réseau écrit en tableau de nombres |
| `Aq` | A fois q | Le résultat du produit de la matrice A par la liste q |
| `Aᵀ` | A transposée | Le même tableau retourné, lignes et colonnes échangées |
| `b` | b | Ce que chaque point du réseau apporte ou consomme |
| `‖x‖` | norme de x | La longueur de la liste x, une façon de mesurer sa taille |
| `‖Aq − b‖` | norme de A q moins b | De combien on rate la règle physique |
| `∇J` | nabla J | Le gradient, la direction de plus forte pente de J |
| `argmin` | argument du minimum | La valeur qui rend l'expression la plus petite |
| `µ` | mu | Deux usages : la moyenne d'une demande, ou le réglage de la pénalité |
| `σ` | sigma minuscule | L'écart-type, la dispersion autour de la moyenne |
| `η` | êta | Le pas d'apprentissage, la taille des enjambées de la descente |
| `κ` | kappa | Le conditionnement, la difficulté numérique du problème |
| `λ` | lambda | Une valeur propre (voir section 7) |
| `diag(c)` | diagonale de c | Un tableau avec les nombres de c sur la diagonale et des zéros ailleurs |

Sur `argmin` précisément, parce que la confusion est fréquente. `min f(x)` désigne la plus
petite valeur atteinte par f. `argmin f(x)` désigne le x qui la produit. Ici on cherche la
répartition, donc le x, donc `argmin`.

---

## 1. Un vecteur, c'est une liste étiquetée

Notre réseau a 13 conduites. Les débits sur ces 13 conduites forment une liste de 13 nombres.
On note cette liste `q`, et on l'appelle un vecteur (liste ordonnée de nombres).

```
q = [  25 , 120 ,  55 ,  20 , ... ]
       ↑     ↑     ↑     ↑
      e1    e2    e3    e4
    R1→Q1 R1→Q2 Q2→Q3 Q3→Q4
```

Ce qui compte, c'est que l'ordre est fixé une fois pour toutes. La case numéro 3 correspond
toujours à la même conduite, pour tout le monde dans le groupe. C'est pour cette raison que
`generate_network.py` fixe l'ordre des nœuds et des arêtes, et que les autres modules doivent
le lire là plutôt que de le redéfinir.

Une erreur d'ordre entre deux membres du groupe ne fait rien planter. Elle donne des résultats
faux qui ressemblent à des résultats justes.

## 2. Une matrice, c'est un tableau de nombres

Un tableau à lignes et colonnes. Notre matrice `A` a 10 lignes (2 réservoirs plus 8 quartiers)
et 13 colonnes (les 13 conduites). On dit qu'elle est de taille 10 × 13.

## 3. Le produit matrice fois vecteur, la seule opération à vraiment maîtriser

C'est l'opération qui revient partout. Elle a une lecture simple.

Pour calculer `Aq`, on traite chaque ligne de A séparément. On prend la ligne, on la met en
face du vecteur q, on multiplie case par case, et on additionne le tout. Le résultat est un
nombre. On recommence pour chaque ligne.

Exemple minuscule, avec 2 lignes et 3 colonnes :

```
A = [ 1   -1    0 ]        q = [ 10 ]
    [ 0    1   -1 ]            [  4 ]
                               [  3 ]

Ligne 1 :  1×10 + (−1)×4 + 0×3  =  10 − 4 + 0  =  6
Ligne 2 :  0×10 +   1×4 + (−1)×3 =   0 + 4 − 3  =  1

Aq = [ 6 ]
     [ 1 ]
```

Le résultat a autant de cases qu'il y a de lignes dans A. Ici 2 lignes, donc 2 cases.

Retenez la règle de taille : une matrice 10 × 13 multipliée par un vecteur de 13 cases donne
un vecteur de 10 cases. Le 13 « s'annule » entre les deux. Si les nombres ne se correspondent
pas, l'opération n'existe pas, et NumPy lèvera une erreur de forme.

## 4. La transposée, `Aᵀ`

On retourne le tableau : la ligne 1 devient la colonne 1, la ligne 2 devient la colonne 2.
Une matrice 10 × 13 devient une matrice 13 × 10.

Pourquoi ça apparaît dans le gradient. Parce que `A` transforme des débits (13 cases) en bilans
par point (10 cases), et que pour revenir de l'espace des points vers l'espace des conduites,
il faut l'opération inverse au sens des tailles. `Aᵀ` transforme 10 cases en 13 cases.

Une façon de le retenir : `A` va des conduites vers les nœuds, `Aᵀ` va des nœuds vers les
conduites.

## 5. Le graphe

### 5.1 Les mots

Un graphe, c'est un ensemble de points et de traits entre ces points. On note `G = (V, E)`.
`V` est l'ensemble des sommets ou nœuds (les points), `E` l'ensemble des arêtes (les traits).

Ici, les nœuds sont les 2 réservoirs R1 et R2, et les 8 quartiers Q1 à Q8. Les arêtes sont
les 13 conduites, numérotées e1 à e13.

Le graphe est orienté (chaque trait a un sens). L'orientation dit dans quel sens on a décidé
que l'eau circule. C'est une convention posée par M1, et elle doit être défendue dans le
rapport, parce qu'elle interdit implicitement l'écoulement inverse.

### 5.2 La connexité

Un graphe est connexe si on peut aller de n'importe quel point à n'importe quel autre en
suivant les traits. Concrètement : aucun quartier n'est coupé du réseau.

Sur un graphe orienté, il existe deux notions. La connexité forte demande de pouvoir faire
l'aller et le retour en respectant les sens. La connexité faible demande seulement que ce soit
possible en ignorant les sens.

Ici c'est la connexité faible qui compte, et le rapport doit dire pourquoi : l'eau descend des
réservoirs vers les quartiers, elle ne remonte pas. Exiger la connexité forte serait exiger
quelque chose que la physique du problème ne demande pas.

### 5.3 Les fragilités

Trois notions différentes, à ne pas mélanger dans le rapport.

Le **degré** d'un nœud, c'est le nombre de traits qui y arrivent. Un quartier de degré 1 n'a
qu'une seule conduite. Si elle casse, il n'a plus rien. Dans notre réseau, Q1 est dans ce cas,
volontairement.

Une **arête pont** (aussi appelée isthme), c'est une conduite dont la disparition couperait le
graphe en deux morceaux. Sa casse peut priver plusieurs quartiers d'un coup, pas seulement un.

Un **point d'articulation**, c'est un nœud dont la disparition couperait le graphe. Un carrefour
par lequel tout passe.

Les trois notions ne désignent pas les mêmes nœuds, et c'est justement ce qui les rend utiles.
Lancé sur notre réseau, `graph_analysis.py` trouve Q1 comme seul nœud de degré 1, deux arêtes
pont (R1 vers Q1 et R1 vers Q2), et trois points d'articulation (R1, Q2 et Q6).

Q1 n'est donc pas un point d'articulation : le retirer ne coupe rien, puisque rien ne transite
par lui. Q2 en est un, parce que toute la branche Q3 puis Q4 passe par lui. Savoir expliquer
cette différence en soutenance vaut mieux que réciter les trois définitions.

### 5.4 Les cycles, et pourquoi ils sont le centre du projet

Un cycle, c'est une boucle : on part d'un point, on suit des traits, on revient au point de
départ sans repasser deux fois par le même trait.

Regardez notre réseau. Pour aller de Q2 à Q4, il y a deux chemins : le long, Q2 vers Q3 puis
Q3 vers Q4 (les conduites e3 et e4), et le court, Q2 vers Q4 directement (la conduite e11).
C'est une boucle au sens du graphe.

Cette boucle est exactement ce qui crée le choix dont parle l'étape 4 du document 01. On peut
faire passer un peu plus par un chemin et un peu moins par l'autre, sans que Q4 s'en aperçoive.
Notre réseau contient 4 boucles de ce type.

Retenez cette phrase pour la soutenance : **sans cycle, pas de choix ; sans choix, pas
d'optimisation ; sans optimisation, pas de projet.**

## 6. La matrice d'incidence, la traduction du dessin en nombres

### 6.1 La construction

Une colonne par conduite, une ligne par nœud. Dans chaque colonne, on écrit :

- `−1` sur la ligne du nœud d'où part la conduite,
- `+1` sur la ligne du nœud où elle arrive,
- `0` partout ailleurs.

Chaque colonne contient donc exactement un `−1`, un `+1`, et rien d'autre. C'est le test
d'intégrité le plus simple, et il est déjà écrit dans `tests/test_graph.py`.

### 6.2 Un exemple complet, à savoir refaire au tableau

Prenons un mini-réseau : un réservoir R, deux quartiers Q1 et Q2, trois conduites.
`e1 : R → Q1`, `e2 : R → Q2`, `e3 : Q1 → Q2`.

```
            e1   e2   e3
     R  [  −1   −1    0  ]
    Q1  [  +1    0   −1  ]
    Q2  [   0   +1   +1  ]
```

Lisez la colonne `e1` : elle part de R (donc `−1` sur la ligne R) et arrive en Q1 (donc `+1`
sur la ligne Q1). Lisez la ligne Q1 : la conduite `e1` y entre, la conduite `e3` en sort.

### 6.3 Ce que veut dire `Aq = b`

Reprenons ce mini-réseau et calculons `Aq` avec des débits `q = [q1, q2, q3]`.

```
Ligne R  :  −q1 − q2         =  ce qui sort de R, compté négativement
Ligne Q1 :  +q1      − q3    =  ce qui entre en Q1 moins ce qui en sort
Ligne Q2 :       +q2 + q3    =  ce qui entre en Q2
```

Chaque ligne dit la même chose : **entrant moins sortant**. Et le vecteur `b` dit à quoi ce
bilan doit être égal.

Pour un quartier, le bilan doit valoir sa consommation. Q1 consomme 25 en moyenne, donc
`b_Q1 = +25`.

Pour un réservoir, le bilan doit valoir ce qu'il injecte, compté à l'envers puisqu'il ne fait
que sortir de l'eau. Si R fournit 500, alors `b_R = −500`.

Le signe de `b` est un piège sérieux. L'inverser ne déclenche aucune erreur, ne fait rien
planter, et donne une solution complètement fausse. C'est pour cette raison que le module
`build_graph.py` demande à M1 de valider l'interprétation physique et à M2 de valider le codage.

### 6.4 Pourquoi les lignes de A somment à zéro

Additionnez les trois lignes de l'exemple, colonne par colonne. Colonne `e1` : `−1 + 1 + 0 = 0`.
Colonne `e2` : `−1 + 0 + 1 = 0`. Colonne `e3` : `0 − 1 + 1 = 0`.

C'est vrai pour toute matrice d'incidence, et pour une raison physique : chaque conduite prend
de l'eau quelque part et la dépose ailleurs, donc elle ne crée ni ne détruit rien à l'échelle
du réseau entier.

Conséquence directe : la dernière ligne de A est toujours déductible des autres. Elle n'apporte
aucune information nouvelle. C'est ce qui mène à la section suivante.

## 7. Rang, noyau, et le fait qu'il y ait plusieurs solutions

### 7.1 Le rang

Le rang d'une matrice, c'est le nombre de lignes réellement indépendantes, celles qui apportent
chacune une information que les autres ne contiennent pas.

Pour une matrice d'incidence, il existe un résultat exact, que M2 doit démontrer et pas
seulement mesurer :

```
rang(A) = n − k
```

où `n` est le nombre de nœuds et `k` le nombre de morceaux séparés du graphe.

Notre réseau est connexe, donc `k = 1`, donc `rang(A) = 10 − 1 = 9`. La matrice a 10 lignes
mais seulement 9 apportent de l'information.

### 7.2 Le noyau

Le noyau de A, c'est l'ensemble des vecteurs `z` tels que `Az = 0`. En langage du problème :
les répartitions de débits qui ne changent absolument rien au bilan de chaque nœud.

Elles ont une interprétation physique très concrète : ce sont les circulations le long des
cycles. Faire tourner de l'eau en rond dans une boucle ne change ce que reçoit personne.

La dimension du noyau vaut :

```
dim(noyau) = nombre de conduites − rang(A) = 13 − 9 = 4
```

Ce nombre s'appelle le nombre cyclomatique du graphe. Il compte les boucles indépendantes.
Notre réseau en a 4.

### 7.3 La conclusion, et c'est la phrase clé du projet

Si `q` est une solution de `Aq = b`, et si `z` est dans le noyau, alors `q + z` est aussi une
solution. Vérifiez : `A(q + z) = Aq + Az = b + 0 = b`.

Il y a donc une infinité de solutions, formant un espace de dimension 4. Toutes acheminent
exactement la même eau aux mêmes quartiers. Elles diffèrent seulement par les chemins empruntés,
et donc par le coût.

C'est ce déficit de rang qui donne au projet sa raison d'être. Le dire ainsi en soutenance vaut
mieux que réciter la formule.

## 8. Le conditionnement, expliqué sans formule d'abord

### 8.1 L'idée

Le conditionnement mesure à quel point un problème amplifie les erreurs. Un problème bien
conditionné : une petite erreur sur les données donne une petite erreur sur le résultat. Un
problème mal conditionné : une erreur minuscule sur les données donne un résultat très
différent.

L'image la plus utile pour la descente de gradient, c'est celle d'une vallée. Si la vallée est
large et ronde, on descend droit vers le fond en quelques pas. Si elle est longue et très
étroite, on rebondit d'un flanc à l'autre en zigzaguant, et il faut beaucoup plus de pas pour
arriver au fond.

Le conditionnement, noté `κ` (kappa), mesure ce rapport entre la largeur et l'étroitesse de la
vallée. Plus il est grand, plus ça zigzague.

### 8.2 Les valeurs propres, juste ce qu'il faut

Une matrice carrée symétrique possède des directions particulières, dans lesquelles elle se
contente d'étirer ou de comprimer sans faire tourner. Les facteurs d'étirement dans ces
directions s'appellent les valeurs propres, notées `λ`.

Pour l'image de la vallée : la plus grande valeur propre correspond à la direction la plus
raide, la plus petite à la direction la plus plate. Le conditionnement est leur rapport.

```
κ = λ_max / λ_min
```

En Python, sur une matrice symétrique, on utilise `numpy.linalg.eigvalsh` et non `eigvals`.
La version `h` (pour hermitienne, autre nom des matrices symétriques réelles) garantit des
valeurs propres réelles. `eigvals` renverrait des valeurs complexes avec des parties imaginaires
numériques minuscules, qui rendraient toute comparaison bancale.

### 8.3 Le piège qui attend M2, et qu'il faut connaître

Sur un réseau connexe avec des cycles, la matrice A est de rang déficient. Sa plus petite
valeur singulière vaut exactement zéro. Donc `numpy.linalg.cond(A)` renvoie l'infini.

Et l'infini ne dit rien. La valeur sort de la définition elle-même, elle ne renseigne en rien
sur le réseau.

Deux quantités ont un sens à la place, et le rapport doit dire laquelle il retient.

**La première**, pour parler de la difficulté à résoudre `Aq = b` : le rapport entre la plus
grande valeur singulière de A et la plus petite qui soit non nulle. Cette quantité est liée à
la connectivité algébrique du graphe, aussi appelée valeur de Fiedler, notée `λ₂`. Quand un
réseau est mal maillé, il est presque coupé en deux, `λ₂` devient très petit, et ce rapport
explose. C'est exactement l'affirmation du sujet sur le lien entre maillage et instabilité.

**La seconde**, pour parler de la vitesse de la descente de gradient : le conditionnement de la
matrice `H = 2C + 2µAᵀA`, qui gouverne la forme de la vallée du problème pénalisé. Celle-là
est toujours inversible dès que les coûts sont strictement positifs, même quand `AᵀA` ne l'est
pas. C'est le terme de coût qui régularise (rend le problème bien posé).

Ce point est un des rares endroits du projet où l'on peut se distinguer. La plupart des groupes
appelleront `numpy.linalg.cond(A)`, liront `inf`, et écriront quelque chose de flou. Savoir
expliquer pourquoi c'est infini et quoi mesurer à la place, c'est de la vraie compréhension.

### 8.4 Ce que mesure l'Expérience 5

On construit plusieurs versions du réseau, de la plus pauvre en conduites à la plus riche, et
on regarde si le conditionnement mesuré et le nombre d'itérations nécessaires évoluent ensemble.

Trois conditions pour que le protocole tienne debout :

toutes les versions doivent rester connexes, sinon le rang change de nature et les
conditionnements comparés ne mesurent plus la même chose ;

`µ`, le pas et la tolérance doivent être identiques d'une version à l'autre ;

si le pas est calculé à partir de la borne théorique, il change mécaniquement avec le
conditionnement, ce qui mélange deux effets. Le rapport doit dire quel protocole est retenu.

---

## Ce qu'il faut savoir refaire au tableau

- Écrire la matrice d'incidence d'un réseau à 3 nœuds et 3 conduites.
- Calculer un produit matrice fois vecteur à la main sur cet exemple.
- Expliquer ce que dit une ligne de `Aq = b` en français.
- Dire pourquoi `rang(A) = n − k` et ce que ça implique sur le nombre de solutions.
- Expliquer le conditionnement avec l'image de la vallée, sans écrire une seule formule.
- Dire pourquoi `numpy.linalg.cond(A)` renvoie l'infini ici, et quoi mesurer à la place.
