# Le projet de bout en bout, sans une seule formule

À lire en premier, et à relire la veille de la soutenance. Tout le reste du dossier
`comprendre/` détaille les étapes racontées ici.

---

## 1. L'histoire

Une société de distribution d'eau alimente huit quartiers, Q1 à Q8, depuis deux réservoirs
R1 et R2 (grands réservoirs de stockage). Entre les réservoirs et les quartiers, il y a des
conduites (tuyaux), et chaque conduite a un débit maximal et un coût.

Aujourd'hui, la société répartit l'eau « à l'ancienne » : chaque quartier reçoit une part
proportionnelle à ce qu'il consomme d'habitude. Un quartier qui consomme le double d'un autre
reçoit le double. Personne n'a jamais vérifié si cette règle est la meilleure.

Deux problèmes avec ça.

Le premier, c'est que cette règle ignore complètement la forme du réseau. Elle décide combien
chaque quartier reçoit, mais pas par quel chemin l'eau y arrive. Or acheminer 200 unités par
une seule conduite ne coûte pas la même chose que 100 par deux conduites différentes.

Le second, c'est que la demande de chaque quartier change tous les jours et qu'on ne la connaît
jamais à l'avance. Une vague de chaleur, une fête de quartier, une coupure chez le voisin qui
reporte sa consommation ailleurs. La règle actuelle est calée sur des moyennes, et les moyennes
ne se produisent presque jamais telles quelles.

L'ingénieur du réseau voudrait un outil qui propose une meilleure répartition, et qui tienne
encore debout les jours où la demande réelle s'écarte des prévisions.

## 2. Ce que le groupe doit livrer

Une comparaison chiffrée entre la répartition actuelle et une répartition optimisée, testée
sur plusieurs scénarios de demande simulés. Rien de plus, rien de moins. Tout le travail
mathématique existe pour produire ce tableau de comparaison et pour pouvoir le défendre.

À côté, un rapport qui démontre tout ce que le code calcule. Le rapport ne contient aucune
ligne de code, seulement du pseudo-code (description d'algorithme en langage courant). Et toute
formule codée doit avoir été dérivée à la main dans le rapport avant d'être tapée au clavier.
Cette règle est notée.

## 3. La chaîne complète, étape par étape

C'est la colonne vertébrale du projet. Si vous ne retenez qu'une chose, retenez cet
enchaînement : chaque étape existe parce que la précédente l'a rendue nécessaire.

### Étape 1. On dessine le réseau

Les réservoirs et les quartiers deviennent des points. Les conduites deviennent des traits
entre les points. Ce dessin s'appelle un graphe (points reliés par des traits).

Le sujet insiste sur ce point : le graphe doit servir d'objet de calcul à part entière. C'est de
lui que tout le reste va sortir.

On vérifie au passage qu'aucun quartier n'est isolé, et on repère les fragilités. Dans notre
réseau, Q1 n'est relié que par une seule conduite, R1 vers Q1. Si elle casse, Q1 n'a plus
d'eau du tout.

### Étape 2. On transforme le dessin en tableau de nombres

Un ordinateur ne sait pas manipuler un dessin. On traduit donc le graphe en un tableau de
nombres qu'on appelle la matrice d'incidence, notée A. Chaque colonne de ce tableau représente
une conduite, chaque ligne représente un point du réseau.

Cette traduction est le pivot de tout le projet. Elle fait passer d'un objet visuel à un objet
calculable.

### Étape 3. On écrit la règle physique de base

À chaque point du réseau, une règle évidente doit être respectée : l'eau qui arrive moins l'eau
qui repart égale l'eau consommée sur place. Un réservoir n'en consomme pas, il en injecte. Un
quartier en consomme.

Écrite avec la matrice A, cette règle tient en une ligne : `Aq = b`. Ici `q` est la liste des
débits sur chaque conduite (ce qu'on cherche), et `b` la liste de ce que chaque point apporte
ou consomme (ce qu'on subit).

### Étape 4. On découvre qu'il y a plusieurs solutions

C'est le moment charnière du projet, et celui qu'il faut savoir expliquer.

Le réseau contient des boucles. Dès qu'il y a une boucle, il existe plusieurs façons différentes
d'acheminer exactement la même eau aux mêmes quartiers. On peut faire passer un peu plus par
la conduite du haut et un peu moins par celle du bas, sans que personne ne reçoive quoi que ce
soit de différent.

Autrement dit, la règle physique ne suffit pas à décider. Elle laisse un choix.

Et c'est précisément ce choix qui rend l'optimisation possible. S'il n'y avait qu'une seule
solution, il n'y aurait rien à optimiser, le projet n'existerait pas.

### Étape 5. On décide quel critère départage les solutions

Parmi toutes les répartitions physiquement possibles, on cherche la moins chère. Le coût d'une
conduite augmente comme le carré de son débit : doubler le débit multiplie le coût par quatre.

Cette forme en carré a une conséquence importante et contre-intuitive. Elle pousse à étaler les
débits plutôt qu'à les concentrer. Faire passer 100 par deux conduites coûte moins que 200 par
une seule, même si la deuxième conduite est un peu plus chère à l'unité. C'est de là que vient
le gain par rapport à la répartition proportionnelle, et c'est aussi de là que vient l'effet
d'équité, sans qu'on l'ait demandé explicitement.

### Étape 6. On a un problème qu'on ne sait pas résoudre directement

On cherche donc la solution la moins chère parmi celles qui respectent la règle physique. En
langage mathématique, c'est un problème d'optimisation sous contrainte (minimiser quelque chose
en respectant une règle).

Le cours n'a vu qu'une méthode de minimisation : la descente de gradient (on descend la pente
petit à petit). Cette méthode ne sait pas gérer une contrainte. Il faut donc transformer le
problème.

### Étape 7. On transforme la contrainte en amende

L'astuce s'appelle la pénalisation. Au lieu d'interdire de violer la règle physique, on rend
la violation coûteuse. On fabrique une nouvelle fonction de coût qui additionne deux choses :
le coût réel de l'acheminement, et une amende proportionnelle à l'écart avec la règle physique.

L'amende est multipliée par un réglage appelé µ (mu). Plus µ est grand, plus tricher coûte cher,
donc plus la solution respecte la règle physique.

Le sujet interdit explicitement l'autre méthode, les multiplicateurs de Lagrange. La raison
tient au programme du cours : la pénalisation garde le problème dans le cadre de la descente
de gradient, tandis que Lagrange demanderait un autre outillage.

### Étape 8. On calcule la pente

Pour descendre une pente, il faut savoir dans quelle direction elle descend. Cette direction
s'appelle le gradient, noté ∇J (nabla J). Le Membre 4 doit le calculer à la main, entièrement,
et le faire relire par deux autres personnes.

Pourquoi tant de précautions. Parce qu'une erreur dans le gradient ne fait pas planter le
programme. Elle produit un résultat faux et parfaitement plausible, qui invalide silencieusement
les six expériences.

### Étape 9. On interdit les débits négatifs

Un débit négatif voudrait dire que l'eau remonte la conduite. Le modèle ne l'autorise pas.
À chaque pas de la descente, si un débit est passé sous zéro, on le remet à zéro. Cette
opération s'appelle une projection.

Piège classique : il faut projeter à chaque pas, pas une seule fois à la fin. Projeter
seulement à la fin donne un autre algorithme, qui ne converge pas vers le même point.

### Étape 10. On simule l'incertitude

Jusqu'ici on a supposé qu'on connaissait la demande. On ne la connaît pas.

On modélise donc la demande de chaque quartier comme une variable aléatoire (une quantité qui
change à chaque tirage), suivant une loi normale (la courbe en cloche). Puis on tire au hasard
1000 journées possibles, et pour chacune on recalcule la répartition optimale. Cette méthode
s'appelle Monte-Carlo (simuler beaucoup de scénarios au hasard).

C'est le cœur du travail du Membre 5.

### Étape 11. On compare

Pour chacune des 1000 journées simulées, on calcule aussi ce qu'aurait donné la répartition
actuelle, celle proportionnelle à la demande. On compare les deux sur trois plans : le coût
total, le respect de la règle physique, et l'équité entre quartiers.

Le résultat le plus intéressant n'est pas forcément que la solution optimisée coûte moins cher
en moyenne. C'est souvent qu'elle varie moins d'un jour à l'autre. Pour un réseau d'eau, la
stabilité vaut au moins autant que le prix moyen, parce que c'est la journée catastrophique qui
coûte, pas la journée moyenne.

### Étape 12. On vérifie que la théorie et l'expérience se rejoignent

Le sujet exige au minimum deux vérifications de ce type. Le groupe en fait deux précises.

La première teste la règle de convergence. La théorie dit que la descente ne converge que si
le pas est inférieur à une certaine valeur. On lance donc des descentes de part et d'autre de
cette valeur, et on regarde si ça se passe comme annoncé.

La seconde teste le lien entre la forme du réseau et la difficulté numérique. La théorie dit
qu'un réseau mal maillé (peu de conduites entre quartiers) rend le calcul instable. On construit
donc plusieurs versions du même réseau, du plus pauvre au plus riche en conduites, et on mesure.

## 4. Les six expériences, en une phrase chacune

| Expérience | Ce qu'elle montre |
|---|---|
| 1 | Sur une journée moyenne, combien la répartition optimisée fait gagner par rapport à l'actuelle |
| 2 | Sur 1000 journées tirées au hasard, laquelle des deux tient le mieux |
| 3 | Ce que change le réglage µ, et pourquoi on ne peut pas simplement le mettre très grand |
| 4 | Que la règle théorique sur le pas d'apprentissage se vérifie vraiment |
| 5 | Qu'un réseau mal maillé est effectivement plus dur à calculer |
| 6 | Quels quartiers consomment régulièrement autrement que prévu |

## 5. Qui fait quoi

| Membre | Sa partie | Ce qu'il doit livrer |
|---|---|---|
| M1 | Le réseau | La topologie figée, le schéma, la section « Formulation du problème » |
| M2 | L'algèbre | La matrice A, son rang, son conditionnement, les preuves écrites |
| M3 | Les probabilités et statistiques | Le modèle de demande, les estimateurs, les intervalles de confiance |
| M4 | L'optimisation | La preuve de convexité, la dérivation du gradient, les conditions de convergence |
| **M5** | **Le code et les expériences** | **Monte-Carlo, le solveur, les 6 expériences, les figures** |
| M6 | La validation et le rapport | La comparaison, le rapport complet, la checklist |

L'ordre dans lequel les gens se débloquent : M1 démarre seul. M2 et M3 partent dès que M1 a
figé le réseau. M4 a besoin du conditionnement calculé par M2 pour finaliser la borne sur le
pas. M5 ne code pas avant que M4 soit relu. M6 attend les résultats de M5.

Le Membre 5 est donc en bout de chaîne côté théorie, et en amont de tout côté résultats. C'est
la position la plus exposée du groupe : si M4 prend du retard, M5 le prend aussi, et M6 après.

## 6. Les trois pièges qui coûtent des points

**Coder avant d'avoir dérivé.** La contrainte méthodologique 1 du sujet l'interdit. Une pull
request qui implémente une formule doit pointer vers la section du rapport où elle est
démontrée.

**Utiliser Lagrange.** Explicitement interdit par la contrainte méthodologique 2. Même en
passant, même en note de bas de page.

**Mettre du code dans le rapport.** Interdit, y compris sous forme de capture d'écran. Le
pseudo-code est accepté, et lui seul.

## 7. Ce que ce projet ne fait pas, et qu'il faut savoir dire

Un jury sérieux cherche les limites. Autant les connaître avant qu'on vous les montre.

Le modèle ne contient aucun terme d'équité dans son objectif. L'équité observée est un effet
de bord du coût quadratique, qui répartit au lieu de concentrer. Le rapport doit l'assumer.

Les capacités des conduites sont dans le fichier de configuration mais ne sont pas imposées au
solveur. Rien n'empêche la solution de dépasser une capacité. Il faut le vérifier après coup et
le signaler.

La loi normale autorise mathématiquement des demandes négatives. Avec les écarts-types retenus,
entre 15 % et 20 % de la moyenne, il faudrait descendre à cinq écarts-types sous la moyenne
pour atteindre zéro. La probabilité vaut 2,9 pour dix millions, mais le rapport doit la
chiffrer plutôt que de balayer la question.

Le réseau est synthétique (inventé, pas mesuré sur le terrain). Le sujet l'autorise
explicitement, à condition de défendre la construction.
