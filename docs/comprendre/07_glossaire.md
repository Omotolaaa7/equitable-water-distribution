# Glossaire

À garder ouvert pendant la lecture des autres documents et pendant les révisions.

---

## 1. Les symboles

| Symbole | Nom | Ce que c'est ici |
|---|---|---|
| `G = (V, E)` | graphe | Le réseau : `V` les points, `E` les conduites |
| `V` | sommets, nœuds | Les 2 réservoirs et les 10 quartiers, soit 12 en tout |
| `E` | arêtes | Les 15 conduites |
| `n` | | Le nombre de nœuds, 12 |
| `k` | | Le nombre de morceaux séparés du graphe, 1 puisque connexe |
| `A` | matrice d'incidence | Le réseau écrit en tableau de nombres, 12 lignes et 15 colonnes |
| `Aᵀ` | A transposée | Le tableau retourné, 15 lignes et 12 colonnes |
| `q` | | Les débits sur chaque conduite, 15 nombres. C'est l'inconnue |
| `q*` | q étoile | La répartition optimale, celle qu'on cherche |
| `q_e` | | Le débit sur la conduite `e` |
| `b` | | Ce que chaque nœud apporte ou consomme, 12 nombres |
| `c_e` | | Le coût unitaire de la conduite `e`, strictement positif |
| `C` | | `diag(c_e)`, les coûts sur la diagonale, zéros ailleurs |
| `D_i` | | La demande du quartier `i`, aléatoire |
| `µ_i` | mu | La demande moyenne du quartier `i` |
| `σ_i` | sigma | L'écart-type de la demande du quartier `i` |
| `σ_i²` | | La variance, le carré de l'écart-type |
| `Σ` | sigma majuscule | Deux usages : une somme, ou la matrice de covariance |
| `ρ` | rho | La corrélation entre deux quartiers, entre −1 et +1 |
| `µ` | mu | Le réglage de la pénalisation. Homonyme de la moyenne, attention |
| `J(q)` | | La fonction de coût pénalisée, celle qu'on minimise |
| `∇J` | nabla J | Le gradient, la liste des 15 dérivées partielles |
| `∂J/∂q_e` | d rond | La dérivée partielle par rapport à un seul débit |
| `H` | hessienne | `2C + 2µAᵀA`, la matrice des dérivées secondes |
| `η` | êta | Le pas d'apprentissage de la descente |
| `L` | | La constante de Lipschitz, plus grande valeur propre de `H` |
| `λ` | lambda | Une valeur propre |
| `λ₂` | | La connectivité algébrique, ou valeur de Fiedler |
| `κ` | kappa | Le conditionnement |
| `P(·)` | | La projection, ici `max(·, 0)` |
| `‖x‖` | norme | La longueur d'une liste de nombres |
| `N` | | Le nombre de tirages Monte-Carlo, 1000 en référence |
| `n` en stats | | La taille de l'échantillon |
| `µ̂`, `σ̂` | chapeau | Valeur estimée à partir des données, par opposition à la vraie |
| `~` | suit la loi | `D_i ~ N(µ, σ²)` se lit « D_i suit une loi normale » |
| `∈` | appartient à | `e ∈ E` se lit « la conduite e fait partie du réseau » |
| `argmin` | | La valeur qui rend l'expression la plus petite |
| `≥`, `≤` | | Supérieur ou égal, inférieur ou égal |
| `→` | tend vers | `µ → ∞` se lit « quand mu devient très grand » |

## 2. Les termes, par ordre alphabétique

**Arête** : un trait du graphe, ici une conduite.

**Arête pont**, ou isthme : une conduite dont la disparition couperait le réseau en deux
morceaux.

**Biais** (d'un estimateur) : l'erreur systématique qu'il commet en moyenne. Un estimateur sans
biais tombe juste en moyenne sur un grand nombre de répétitions.

**Cholesky** (factorisation de) : la décomposition `Σ = L Lᵀ` qui permet de tirer des demandes
corrélées. Elle échoue si la matrice de covariance n'est pas semi-définie positive.

**Composante connexe** : un morceau du graphe dont tous les points sont reliés entre eux.

**Conditionnement** : la mesure de la fragilité numérique d'un problème. L'image de la vallée :
plus elle est étroite et longue, plus le conditionnement est grand et plus la descente zigzague.

**Connexité** : la propriété qu'aucun point ne soit isolé. Faible si on ignore le sens des
flèches, forte si on les respecte. Ici c'est la faible qui compte.

**Contrainte** : une règle que la solution doit respecter. Ici deux : la conservation des flux,
et la positivité des débits.

**Convexe** : en forme de bol, avec un seul fond. Garantit que la descente de gradient arrive au
bon endroit, où qu'elle parte.

**Corrélation** : la mesure du lien entre deux quantités aléatoires, entre −1 et +1.

**Covariance** : la même idée que la corrélation, mais non normalisée. `Σ_ij = ρ_ij σ_i σ_j`.

**Cycle** : une boucle dans le graphe. C'est ce qui crée le choix entre plusieurs répartitions
possibles.

**ddof** : le paramètre de NumPy qui décide du diviseur de la variance. Il faut `ddof=1` pour
la variance empirique corrigée.

**Degré** d'un nœud : le nombre de conduites qui y arrivent. Un quartier de degré 1 est fragile.

**Dérivée partielle** : la pente selon une seule variable, les autres étant gelées.

**Descente de gradient** : la méthode qui consiste à faire des pas dans le sens de la pente
descendante, jusqu'à atteindre le fond.

**Différences finies** : la vérification numérique d'un gradient, en bougeant une composante
d'un cheveu et en mesurant la variation.

**Espérance** : la moyenne théorique d'une variable aléatoire.

**Estimateur** : une recette qui part des données observées et produit une valeur approchée
d'une quantité inconnue.

**Fiedler** (valeur de) : la deuxième plus petite valeur propre du laplacien du graphe, notée
`λ₂`. Elle mesure à quel point le réseau est loin d'être coupé en deux. Petite valeur, réseau
mal maillé.

**Gradient** : la liste des dérivées partielles. Pointe vers la montée la plus raide, donc son
opposé pointe vers la descente.

**Hessienne** : la matrice des dérivées secondes. Ici elle vaut `2C + 2µAᵀA` et ne dépend pas
de `q`, parce que `J` est quadratique.

**Intervalle de confiance** : une fourchette construite sur les données, telle que si on
répétait l'expérience un grand nombre de fois, 95 % des fourchettes contiendraient la vraie
valeur.

**Lagrange** (multiplicateurs de) : l'autre méthode pour traiter une contrainte d'égalité.
Explicitement interdite par le sujet.

**Laplacien** du graphe : la matrice `AAᵀ`. Ses valeurs propres renseignent sur la connectivité.

**Lipschitz** (constante de) : `L`, le facteur qui borne la vitesse de variation du gradient.
Fixe le pas maximal via `η < 2/L`.

**Loi des grands nombres** : plus on fait de tirages, plus la moyenne calculée se rapproche de
la vraie moyenne.

**Loi normale** : la courbe en cloche. 68 % des valeurs à un écart-type, 95 % à deux, 99,7 % à
trois.

**Matrice** : un tableau de nombres à lignes et colonnes.

**Matrice d'incidence** : la traduction du graphe en tableau. Une colonne par conduite, avec un
`−1` au départ et un `+1` à l'arrivée.

**Monte-Carlo** : simuler un grand nombre de scénarios au hasard pour estimer ce qu'on ne sait
pas calculer directement.

**Nombre cyclomatique** : le nombre de boucles indépendantes du graphe. Vaut `|E| − n + k`,
soit 4 ici.

**Norme** : la longueur d'une liste de nombres. `‖Aq − b‖` mesure de combien on rate la
conservation.

**Noyau** d'une matrice : l'ensemble des vecteurs qu'elle envoie sur zéro. Ici, les circulations
en boucle qui ne changent le bilan d'aucun nœud.

**Orienté** (graphe) : chaque arête a un sens. Ici, le sens d'écoulement supposé de l'eau.

**Pénalisation** : remplacer une contrainte par une amende dans la fonction de coût. La méthode
imposée par le sujet.

**p-valeur** : la probabilité d'observer un écart au moins aussi grand que celui mesuré, si en
réalité les deux stratégies se valaient. Elle ne dit pas que l'écart est important.

**Point d'articulation** : un nœud dont la disparition couperait le graphe.

**Projection** : ramener un point dans le domaine autorisé, au plus proche. Ici `max(q, 0)`.

**Quantile** : la valeur en dessous de laquelle tombe une proportion donnée des observations.
Le quantile à 95 % est dépassé une fois sur vingt.

**Rang** d'une matrice : le nombre de lignes réellement indépendantes. Pour une matrice
d'incidence, `n − k`.

**Semi-définie positive** : une matrice dont toutes les valeurs propres sont positives ou
nulles. Condition pour qu'une matrice de covariance décrive une vraie loi gaussienne.

**Student** (loi de) : la loi à utiliser pour un intervalle de confiance quand l'écart-type est
estimé et non connu.

**Test apparié** : un test statistique qui compare deux séries mesurées sur les mêmes cas.
Obligatoire ici, puisque les deux stratégies tournent sur les mêmes scénarios.

**Théorème central limite** : une somme de nombreuses petites quantités indépendantes tend vers
une loi normale.

**Transposée** : le tableau retourné, lignes et colonnes échangées.

**Valeur propre** : le facteur d'étirement d'une matrice dans une de ses directions
particulières.

**Valeur singulière** : la version qui s'applique aux matrices non carrées. Racine carrée des
valeurs propres de `AAᵀ`.

**Variable aléatoire** : une quantité dont la valeur change à chaque observation, avec une loi
connue.

**Variance** : le carré de l'écart-type. Mesure la dispersion.

---

## 3. Les chiffres du projet, à connaître par cœur

| Quantité | Valeur |
|---|---|
| Réservoirs | 2 |
| Quartiers | 10 |
| Nœuds au total | 12 |
| Conduites | 15 |
| Rang de A | 11 |
| Dimension du noyau, ou nombre de boucles | 4 |
| Offre totale | 1060 m³/h |
| Demande moyenne totale | 1060 m³/h |
| Coefficient de variation des demandes | de 12 % à 28 % |
| Corrélations déclarées | 0,40 puis 0,35 puis 0,30 |
| Tirages Monte-Carlo de référence | 1000 |
| Échelles vérifiées | 100, 1000, 10 000 |
| Graine aléatoire | 42 |
| Valeurs de µ testées | 1, 10, 100, 1000 |
| Quartier fragile | Q10, degré 1 |
| Expériences imposées | 6 |
| Sections obligatoires du rapport | 9 |
| Volets du développement mathématique | 5 |
| Points du jalon avant de coder l'optimisation | 8 |

## 4. Les poids de la grille de notation

| Rubrique | Poids | Qui la porte |
|---|---|---|
| Formulation du problème | 10 % | M1 |
| Algèbre linéaire | 15 % | M2 |
| Probabilités et statistiques | 20 % | M3 |
| Optimisation | 20 % | M4 |
| Mathématiques discrètes | 10 % | M1 et M2 |
| Implémentation et validation | 15 % | M5 et M6 |
| Rédaction et rigueur | 10 % | M6 |
