# Les maths depuis zéro, partie 3 : l'optimisation

Couvre la rubrique « Optimisation », 20 % de la note. C'est le document à maîtriser le mieux,
parce que c'est celui dont le Membre 5 tire le code, et parce que c'est là que le jury posera
ses questions les plus précises.

---

## 1. Minimiser une fonction, l'idée de base

### 1.1 Une fonction

Une fonction, c'est une machine : on lui donne une valeur, elle en rend une autre. On écrit
`f(x) = x²`. Si on lui donne 3, elle rend 9.

Ici, notre machine s'appelle `J`. On lui donne une répartition de débits `q`, elle rend un
nombre : le coût de cette répartition. On cherche la répartition qui rend ce nombre le plus
petit possible.

### 1.2 La dérivée, c'est la pente

Pour une fonction d'une seule variable, la dérivée en un point donne la pente de la courbe à
cet endroit.

Dérivée positive : la courbe monte, il faut aller à gauche pour descendre.
Dérivée négative : la courbe descend, il faut aller à droite.
Dérivée nulle : on est à plat, potentiellement au fond.

Les deux dérivées à connaître pour tout ce projet :

```
si f(x) = x²        alors  f'(x) = 2x
si f(x) = a x²      alors  f'(x) = 2 a x
```

Tout le gradient du projet se déduit de ces deux lignes, plus la règle de composition.

### 1.3 La dérivée partielle

Notre fonction `J` ne dépend pas d'une seule variable mais de 13, un débit par conduite.

La dérivée partielle par rapport à `q_3`, notée `∂J/∂q_3`, se calcule en gelant les 12 autres
variables et en dérivant comme si `q_3` était la seule.

Le symbole `∂` (d rond) sert uniquement à signaler qu'on gèle le reste. La mécanique de calcul
est celle d'une dérivée ordinaire.

### 1.4 Le gradient

Le gradient, noté `∇J` (nabla J), c'est simplement la liste des 13 dérivées partielles, rangées
dans l'ordre.

```
∇J(q) = [ ∂J/∂q_1 , ∂J/∂q_2 , ... , ∂J/∂q_13 ]
```

Sa lecture géométrique : il pointe dans la direction où `J` augmente le plus vite. Donc `−∇J`
pointe vers la descente la plus raide. C'est toute l'idée de la descente de gradient.

L'image du randonneur dans le brouillard marche bien. On ne voit pas la vallée, mais on sent la
pente sous ses pieds. On fait un pas dans le sens de la descente, on re-sent la pente, on
recommence.

## 2. La convexité, et pourquoi elle sauve le projet

### 2.1 L'idée

Une fonction est convexe si son graphe a la forme d'un bol : elle descend, puis remonte, sans
jamais faire de creux secondaire.

Le test visuel : si on relie deux points quelconques de la courbe par un segment, le segment
reste au-dessus de la courbe.

### 2.2 Pourquoi ça compte

Sur une fonction non convexe, une descente de gradient peut se coincer dans un creux local, un
fond de vallée qui n'est pas le plus bas de tous. Et rien ne permet de savoir qu'on s'est
coincé.

Sur une fonction convexe, il n'y a qu'un seul fond. Où qu'on parte, la descente arrive au bon
endroit.

C'est pour cette raison que le sujet exige une proposition mathématique justifiée, et que le
candidat naturel est la convexité de `J`.

### 2.3 La démonstration, en trois temps

**Le terme de coût.** `Σ c_e q_e²` s'écrit aussi `qᵀCq` où `C = diag(c_e)`, une matrice qui
porte les coûts sur sa diagonale et des zéros ailleurs. Cette forme est strictement convexe dès
que tous les `c_e` sont strictement positifs.

L'intuition sans matrice : c'est une somme de paraboles `c_e q_e²`, chacune tournée vers le
haut parce que `c_e > 0`. Une somme de bols est un bol.

**Le terme de pénalité.** `µ‖Aq − b‖²` est convexe pour tout `µ ≥ 0`. C'est un carré, donc
toujours positif, et la composition d'une fonction affine avec un carré reste convexe.

**La somme.** Une somme de deux fonctions convexes est convexe.

Le point à ne surtout pas escamoter : la conclusion repose entièrement sur `c_e > 0`. Ce n'est
pas une précaution d'hygiène de code, c'est l'hypothèse exacte dont dépend la démonstration.
Si un coût était nul, la stricte convexité tomberait. C'est la raison pour laquelle
`valider_reseau` vérifie ce point en premier.

## 3. Le problème, et pourquoi on ne peut pas le résoudre tel quel

Le problème s'écrit :

```
q* = argmin_q  Σ_{e∈E} c_e q_e²      sous     Aq = b ,   q ≥ 0
```

En français : trouver la répartition `q` la moins chère, parmi celles qui respectent la
conservation des flux et qui n'ont aucun débit négatif.

Le mot « sous » signale des contraintes. Et la descente de gradient ne sait pas gérer de
contrainte : elle descend là où la pente l'emmène, sans regarder si elle sort du domaine
autorisé.

Il faut donc transformer le problème. Les deux contraintes sont traitées différemment.

## 4. La pénalisation, pour la contrainte d'égalité

### 4.1 L'idée

Au lieu d'interdire de violer `Aq = b`, on rend la violation coûteuse. On ajoute au coût une
amende proportionnelle au carré de l'écart :

```
J(q) = Σ_e c_e q_e²  +  µ ‖Aq − b‖²
       └── coût réel ──┘  └── amende ──┘
```

`µ` règle la sévérité de l'amende. Grand `µ`, tricher coûte cher, la solution respecte bien la
conservation. Petit `µ`, la solution privilégie le coût et néglige la physique.

### 4.2 Ce qu'il faut savoir dire sur le compromis

Quand `µ` tend vers l'infini, la solution pénalisée tend vers la vraie solution contrainte. On
pourrait donc croire qu'il suffit de mettre `µ` très grand.

Sauf que grandir `µ` étire la vallée dans certaines directions et pas dans d'autres, ce qui
dégrade le conditionnement, ce qui impose un pas plus petit, ce qui ralentit la convergence.

Les deux effets ont la même origine algébrique : ils sortent tous les deux de la matrice
`2C + 2µAᵀA`. Ce n'est pas une coïncidence expérimentale, et le rapport doit le présenter ainsi.

C'est exactement ce que mesure l'Expérience 3, avec `µ` valant successivement 1, 10, 100 et 1000.

### 4.3 Pourquoi pas Lagrange

Le sujet l'interdit explicitement, contrainte méthodologique 2. La raison affichée : rester dans
le cadre de la descente de gradient vue en cours.

Si le jury demande ce qu'aurait donné Lagrange, la réponse honnête est qu'on aurait obtenu la
contrainte satisfaite exactement au lieu d'approximativement, au prix d'un système à résoudre
qui sort du cours. Ne pas prétendre que la pénalisation est supérieure : elle est imposée, et
elle approche.

## 5. La projection, pour la contrainte de positivité

### 5.1 L'idée

Après chaque pas de descente, si un débit est devenu négatif, on le remet à zéro. Les autres ne
bougent pas.

```
P(q)_e = max(q_e , 0)
```

### 5.2 Pourquoi c'est bien « la » projection, et pas un bricolage

La projection euclidienne d'un point sur un ensemble, c'est le point de l'ensemble le plus
proche. Il faut donc montrer que `max(q, 0)` donne bien le point le plus proche dans le domaine
`q ≥ 0`.

La démonstration, à savoir refaire. On cherche le `y ≥ 0` qui minimise `‖y − q‖²`. Or

```
‖y − q‖² = Σ_e (y_e − q_e)²
```

Chaque terme de la somme ne dépend que d'une seule composante. Le problème se sépare donc en
13 problèmes indépendants, et chacun s'écrit : trouver `y_e ≥ 0` qui minimise `(y_e − q_e)²`.

Si `q_e ≥ 0`, le minimum est atteint en `y_e = q_e`, avec une distance nulle.
Si `q_e < 0`, la fonction est croissante sur les `y_e ≥ 0`, donc le minimum est en `y_e = 0`.

Dans les deux cas, `y_e = max(q_e, 0)`.

Ce qui rend la projection aussi simple, c'est la séparabilité (chaque composante indépendante
des autres). Elle ne le serait plus sur un ensemble qui couple les composantes, comme les
contraintes de capacité `q_e ≤ cap_e` si le groupe décidait de les activer.

### 5.3 L'erreur à ne pas commettre

Projeter à chaque itération, pas une seule fois à la fin. La section 14 du plan la liste
explicitement.

Projeter à la fin donne un autre algorithme. Ça revient à laisser la descente explorer
librement une zone interdite, puis à écraser le résultat sur la frontière. Le point d'arrivée
diffère.

## 6. La dérivation du gradient, pas à pas

C'est le passage à savoir refaire seule, sans notes. Le sujet exige une dérivation complète, et
le plan demande deux relecteurs.

### 6.1 Ce qu'on cherche

```
J(q) = Σ_e c_e q_e²  +  µ Σ_i ( (Aq)_i − b_i )²
```

On veut `∂J/∂q_f` pour une conduite `f` quelconque. Une fois qu'on l'a pour une conduite
quelconque, on l'a pour toutes.

### 6.2 Premier terme

```
∂/∂q_f  [ Σ_e c_e q_e² ]
```

Dans cette somme, tous les termes où `e ≠ f` sont des constantes vis-à-vis de `q_f`, puisqu'on
gèle les autres variables. Leur dérivée est nulle. Il ne reste que le terme `e = f` :

```
∂/∂q_f [ c_f q_f² ] = 2 c_f q_f
```

**Résultat du premier terme : `2 c_f q_f`.**

### 6.3 Deuxième terme

```
∂/∂q_f  [ µ Σ_i ( (Aq)_i − b_i )² ]
```

Ici, on ne peut pas éliminer de termes aussi vite, parce que `q_f` peut intervenir dans
plusieurs lignes `i` à la fois.

**Étape a.** Que vaut `(Aq)_i` ? C'est la ligne `i` de A multipliée par `q` :

```
(Aq)_i = Σ_e A[i,e] q_e
```

**Étape b.** Sa dérivée par rapport à `q_f` ? Un seul terme de la somme contient `q_f`, celui
où `e = f`, et il vaut `A[i,f] q_f`. Sa dérivée est donc :

```
∂(Aq)_i / ∂q_f = A[i,f]
```

Un simple coefficient de la matrice. C'est l'étape que les gens sautent, et c'est la seule qui
demande de réfléchir.

**Étape c.** On dérive le carré, avec la règle de composition. Pour une fonction `u(q_f)` :

```
∂/∂q_f [ u² ] = 2 u × ∂u/∂q_f
```

Ici `u = (Aq)_i − b_i`. Le terme `b_i` est une constante, sa dérivée est nulle. Donc :

```
∂/∂q_f [ ((Aq)_i − b_i)² ] = 2 ((Aq)_i − b_i) × A[i,f]
```

**Étape d.** On somme sur toutes les lignes `i`, et on remet le `µ` :

```
∂/∂q_f [ deuxième terme ] = 2 µ Σ_i A[i,f] ((Aq)_i − b_i)
```

**Étape e.** Reconnaître ce qu'est cette somme. `Σ_i A[i,f] × (quelque chose)_i`, c'est la
colonne `f` de A multipliée par un vecteur. Or multiplier par les colonnes de A, c'est
exactement multiplier par `Aᵀ`. Donc :

```
Σ_i A[i,f] ((Aq)_i − b_i) = ( Aᵀ(Aq − b) )_f
```

**Résultat du deuxième terme : `2 µ ( Aᵀ(Aq − b) )_f`.**

C'est de cette étape que sort la transposée. Elle tombe du calcul, aucune convention n'a été
posée pour la faire apparaître.

### 6.4 Le résultat

En rassemblant, pour toute conduite `f` :

```
∂J/∂q_f = 2 c_f q_f + 2 µ ( Aᵀ(Aq − b) )_f
```

Et en empilant les 13 composantes dans un vecteur :

```
∇J(q) = 2 C q + 2 µ Aᵀ (Aq − b)        avec C = diag(c_e)
```

### 6.5 Vérifier qu'on ne s'est pas trompé, sans faire confiance à personne

Trois erreurs classiques, listées en section 14 du plan : oublier un facteur 2, écrire `A` au
lieu de `Aᵀ`, inverser le signe de `b`.

Aucune des trois ne fait planter le programme. Elles produisent toutes un résultat faux et
plausible.

La parade s'appelle la vérification par différences finies. On compare le gradient calculé par
la formule au gradient estimé numériquement, en bougeant une composante d'un cheveu :

```
∂J/∂q_f  ≈  [ J(q + h·e_f) − J(q − h·e_f) ] / (2h)
```

où `e_f` est un vecteur de zéros avec un seul 1 à la position `f`, et `h` vaut typiquement
`1e-6`.

Utiliser la différence centrée, avec le `+h` et le `−h`, et pas la version décentrée. Son erreur
décroît comme `h²` au lieu de `h`, ce qui permet de distinguer une vraie erreur de dérivation
du simple bruit d'arrondi.

Si l'écart relatif maximal dépasse `1e-6`, il y a une erreur dans la formule ou dans le code.

Cette vérification ne remplace pas la dérivation à la main exigée par le sujet. Elle la contrôle.
Un gradient qui passe le test mais qui n'est pas dérivé dans le rapport reste une violation de
la contrainte méthodologique 1.

## 7. La descente de gradient projetée

### 7.1 L'algorithme complet

```
Entrées : A, b, c, µ, η, q_0, tolérance, k_max

Pour k = 0, 1, 2, ... :
    g_k      ←  ∇J(q_k)  =  2 C q_k + 2 µ Aᵀ(A q_k − b)
    q_{k+1}  ←  P( q_k − η g_k )          avec  P(x) = max(x, 0)
    arrêter si ‖q_{k+1} − q_k‖ < tolérance   ou   k = k_max

Sortie : q_k
```

Cinq lignes. Tout le reste du document sert à justifier ces cinq lignes.

Le point de départ `q_0` est le vecteur nul, qui a l'avantage d'être déjà admissible pour la
contrainte `q ≥ 0`.

### 7.2 Le pas d'apprentissage `η`

`η` (êta) décide de la taille des enjambées. Trop petit, on met un temps fou. Trop grand, on
saute par-dessus le fond de la vallée et on remonte sur l'autre flanc, de plus en plus haut.

Il existe une valeur seuil au-delà de laquelle la divergence est garantie.

### 7.3 La constante de Lipschitz et la borne `η < 2/L`

`J` est quadratique, donc son gradient est une fonction linéaire de `q`, et la matrice qui le
gouverne ne dépend pas de `q`. Cette matrice est la hessienne (matrice des dérivées secondes) :

```
H = 2 C + 2 µ AᵀA
```

`L` est sa plus grande valeur propre. La théorie de la descente de gradient sur une fonction
convexe à gradient lipschitzien donne la condition :

```
η  <  2 / L
```

En pratique, on prend souvent `η = 1/L`, qui est dans la zone stable et loin du seuil.

Sur notre réseau, le calcul est déjà fait et les chiffres sont parlants.

| `µ` | `L` | pas maximal `2/L` |
|---|---|---|
| 1 | 14,95 | 0,134 |
| 10 | 127,4 | 0,0157 |
| 100 | 1 252 | 0,00160 |
| 1 000 | 12 501 | 0,000160 |

Multiplier `µ` par 1 000 divise le pas autorisé par 836. C'est le ralentissement dont parle
la section 4.2, mesuré sur le vrai réseau.

Pour calculer `L`, utiliser `numpy.linalg.eigvalsh(H).max()` et non `eigvals`, parce que `H`
est symétrique.

### 7.4 Ce que fait l'Expérience 4

Elle teste cette borne. On lance des descentes avec plusieurs pas, certains sous `2/L`,
certains au-dessus, et on trace `J(q_k)` en fonction du numéro d'itération.

Le balayage recommandé encadre franchement le seuil, par exemple `η` valant successivement
0,1 puis 0,5 puis 0,9 puis 1,1 puis 1,5 fois `2/L`. Un balayage qui reste entièrement d'un côté
du seuil ne démontre rien.

Deux précautions pratiques. Prévoir un garde-fou de dépassement numérique, parce qu'au-delà du
seuil, `J` part en overflow en quelques dizaines d'itérations et remplit la sortie de `inf` et
de `nan`. Et tracer `J` en échelle logarithmique, faute de quoi les courbes divergentes
écrasent visuellement les courbes convergentes.

L'erreur à ne pas commettre, elle aussi dans la section 14 : présenter une courbe qui descend
comme preuve de convergence. Ce qui est démontré ici, c'est le lien entre la constante de
Lipschitz calculée à partir de A et le comportement observé de part et d'autre du seuil.

### 7.5 Le critère d'arrêt, et pourquoi il n'est pas celui qu'on croit

Sur un problème sans contrainte, on s'arrête quand le gradient devient petit, puisqu'au fond de
la vallée la pente est nulle.

Ici, ça ne marche pas. À l'optimum, certaines conduites ont un débit nul, coincé contre la
frontière `q_e = 0`. Pour ces composantes, le gradient pousse encore vers l'extérieur du domaine
autorisé, et la projection l'annule à chaque fois. Le gradient ne tend donc pas vers zéro.

Le bon critère porte sur le déplacement : on s'arrête quand `q` ne bouge plus.

```
‖q_{k+1} − q_k‖  <  tolérance
```

Ce critère capte le point fixe de l'itération projetée, c'est-à-dire le moment où appliquer un
pas de plus ne change rien.

C'est une subtilité, et c'est précisément le genre de chose qu'un jury vérifie pour distinguer
qui a compris de qui a recopié. Autant la préparer.

## 8. Le lien avec le conditionnement

Plus la vallée est étroite dans une direction et large dans une autre, plus la descente zigzague
et plus il faut d'itérations.

Ce rapport entre le plus raide et le plus plat, c'est le conditionnement de `H`. Il dépend de
`µ` : augmenter `µ` augmente `λ_max`, donc augmente `κ`, donc ralentit.

Il dépend aussi de la structure du réseau, via `AᵀA`. C'est le lien que l'Expérience 5 vérifie,
et le détail du piège sur `numpy.linalg.cond(A)` est expliqué dans
[02_maths_graphe_et_algebre.md](02_maths_graphe_et_algebre.md), section 8.3.

---

## Ce qu'il faut savoir refaire au tableau

- Écrire `J(q)` et dire en français ce que fait chacun de ses deux termes.
- Démontrer que `J` est convexe, en nommant l'hypothèse `c_e > 0` au bon endroit.
- Dériver `∇J(q)` en partant de zéro, en passant par les cinq étapes de la section 6.3.
- Expliquer d'où sort la transposée dans `Aᵀ(Aq − b)`.
- Démontrer que `max(q, 0)` est bien la projection euclidienne sur `q ≥ 0`.
- Écrire les cinq lignes de l'algorithme.
- Dire pourquoi `η < 2/L` et ce qui se passe au-delà.
- Dire pourquoi le critère d'arrêt porte sur le déplacement et non sur la norme du gradient.
