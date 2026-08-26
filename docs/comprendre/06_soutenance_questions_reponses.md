# Préparation à la soutenance

Les questions qu'un jury pose, avec la réponse à donner. Les réponses sont écrites pour être
dites à voix haute, pas récitées.

---

## 1. La présentation du projet en trois durées

Savoir raconter le projet en 30 secondes, en 2 minutes et en 10 minutes. Les trois versions ne
sont pas la même chose raccourcie, elles s'arrêtent à des profondeurs différentes.

### En 30 secondes

> Une société d'eau alimente dix quartiers depuis deux réservoirs. Elle répartit l'eau
> proportionnellement à la consommation habituelle, sans jamais avoir vérifié si c'était le
> meilleur choix. Nous avons construit un outil qui calcule la répartition la moins chère
> compatible avec la physique du réseau, et qui la teste sur mille journées simulées pour voir
> si elle tient quand la demande s'écarte des prévisions.

### En 2 minutes

Ajouter la chaîne : le réseau devient un graphe, le graphe devient une matrice, la matrice donne
une équation de conservation, cette équation a plusieurs solutions à cause des boucles, on
choisit la moins chère, on transforme la contrainte en pénalité pour pouvoir descendre le
gradient, on projette pour interdire les débits négatifs, et on refait tout ça mille fois avec
des demandes tirées au hasard.

### En 10 minutes

Le document [01_le_projet_sans_maths.md](01_le_projet_sans_maths.md), section 3, dans l'ordre.

---

## 2. Les questions de compréhension générale

**« Pourquoi ce projet a-t-il un sens ? Pourquoi n'y a-t-il pas une seule bonne réponse
évidente ? »**

> Parce que le réseau contient des boucles. Dès qu'il y a une boucle, il existe plusieurs
> chemins pour amener la même eau au même quartier. La conservation des flux ne suffit donc pas
> à décider, elle laisse un espace de solutions. Dans notre réseau, cet espace est de dimension
> 4. C'est ce choix résiduel que l'optimisation tranche, en retenant la répartition la moins
> chère.

C'est la meilleure réponse d'ouverture du projet. Elle montre qu'on a compris le lien entre la
structure discrète et l'optimisation, ce qui est justement ce que la grille cherche.

**« En quoi votre graphe n'est-il pas décoratif ? »**

> Il produit la matrice d'incidence, qui produit l'équation de conservation, qui produit le
> terme de pénalisation, dont on dérive le gradient. Si on retirait le graphe, il ne resterait
> rien à optimiser. Et la dimension de l'espace des solutions se lit directement sur le graphe :
> c'est son nombre de boucles indépendantes.

**« Qu'est-ce qui vous dit que votre solution est meilleure ? »**

> Trois mesures, pas une. Le coût technique total, la violation résiduelle de la conservation,
> et la dispersion des taux de satisfaction entre quartiers. Et sur mille scénarios, avec un
> test statistique apparié pour vérifier que l'écart n'est pas dans le bruit de la simulation.

---

## 3. Les questions sur le graphe et l'algèbre

**« Quelle convention avez-vous prise pour la matrice d'incidence ? »**

> Plus un si l'arête entre dans le nœud, moins un si elle en sort, zéro sinon. Avec cette
> convention, chaque ligne de `Aq = b` s'écrit « entrant moins sortant égale consommé ». Pour
> un quartier, `b` vaut sa demande. Pour un réservoir, `b` vaut moins son offre, puisqu'il
> injecte au lieu de consommer.

**« Que vaut le rang de votre matrice, et pourquoi ? »**

> Onze. La règle est `rang(A) = n − k`, avec `n` le nombre de nœuds et `k` le nombre de
> composantes connexes. Nous avons douze nœuds et un réseau connexe, donc onze. La raison est
> physique : chaque colonne contient un plus un et un moins un, donc les lignes somment à zéro,
> donc la dernière est déductible des autres.

**« Que représente le noyau de A ? »**

> Les circulations le long des boucles. Faire tourner de l'eau en rond dans un cycle ne change
> le bilan d'aucun nœud. Sa dimension vaut le nombre de conduites moins le rang, soit quinze
> moins onze égale quatre. C'est le nombre de boucles indépendantes du réseau.

**« Quel est le conditionnement de votre matrice A ? »**

C'est la question piège de la partie algèbre. La mauvaise réponse est de donner un nombre.

> Infini, si on prend la définition usuelle. A est de rang déficient sur un réseau connexe avec
> des cycles, sa plus petite valeur singulière vaut exactement zéro, et `numpy.linalg.cond`
> renvoie l'infini. Ce n'est pas exploitable.
>
> Deux quantités ont un sens à la place. Pour parler de la difficulté à résoudre `Aq = b`, le
> rapport entre la plus grande valeur singulière et la plus petite non nulle, qui est lié à la
> connectivité algébrique du graphe. Pour parler de la vitesse de la descente de gradient, le
> conditionnement de la hessienne `2C + 2µAᵀA`, qui est toujours inversible dès que les coûts
> sont strictement positifs.

**« Expliquez-moi le conditionnement comme si je n'y connaissais rien. »**

> Imaginez une vallée. Si elle est large et ronde, on descend droit au fond en quelques pas. Si
> elle est longue et très étroite, on rebondit d'un flanc à l'autre en zigzaguant et il faut
> beaucoup plus de pas. Le conditionnement mesure ce rapport entre la largeur et l'étroitesse.
> Plus il est grand, plus le calcul zigzague et plus il est fragile aux erreurs d'arrondi.

---

## 4. Les questions sur les probabilités et les statistiques

**« Pourquoi une loi normale ? »**

> Le sujet l'impose, mais l'argument tient. La demande d'un quartier est la somme de centaines
> de consommations individuelles, chacune petite devant le total et à peu près indépendante des
> autres. Le théorème central limite dit qu'une telle somme se rapproche d'une loi normale,
> quelle que soit la forme de chaque terme.

**« Et si les foyers ne sont pas indépendants ? »**

> Alors le théorème ne s'applique plus. Un jour de match ou de coupure générale, tout le monde
> agit ensemble et l'hypothèse tombe. C'est une limite que nous mentionnons dans le rapport.

**« Votre loi normale autorise des demandes négatives. »**

> Oui, mathématiquement. Avec nos écarts-types, entre douze et vingt-huit pour cent de la
> moyenne, il faudrait descendre à plus de trois écarts-types sous la moyenne, ce qui arrive
> moins d'une fois sur mille. Nous le chiffrons dans le rapport. Le Thème 4 du même énoncé
> impose d'ailleurs une loi tronquée ou log-normale pour cette raison précise.

**« Pourquoi divisez-vous par n moins un ? »**

> Parce que les écarts sont mesurés par rapport à une moyenne qui a déjà été calculée sur les
> mêmes données. Ça les rend systématiquement un peu trop petits. Diviser par n moins un
> compense exactement ce rétrécissement, c'est la correction de Bessel. Sans elle, l'estimateur
> de variance est biaisé.

**« Pourquoi Student et pas la loi normale pour vos intervalles de confiance ? »**

> Parce que nous n'utilisons pas le vrai écart-type, nous l'estimons lui aussi. Cette estimation
> ajoute de l'incertitude, et la loi correcte devient celle de Student à n moins un degrés de
> liberté. Sur mille tirages l'écart numérique est négligeable, mais le choix se justifie.

**« Que signifie exactement votre intervalle de confiance à 95 % ? »**

Piège classique.

> Que si on répétait toute l'expérience un grand nombre de fois, quatre-vingt-quinze pour cent
> des intervalles ainsi construits contiendraient la vraie valeur. La formulation courante,
> « il y a 95 % de chances que µ soit dedans », est fausse au sens strict : µ désigne une
> valeur fixe, et c'est l'intervalle qui bouge d'un échantillon à l'autre.

**« Pourquoi un test apparié ? »**

> Parce que les deux stratégies sont évaluées sur les mêmes mille scénarios. Chaque coût
> optimisé a son jumeau du côté de la référence. Un test à deux échantillons indépendants
> ignorerait cet appariement et serait moins puissant, en plus d'être une erreur de méthode.

**« Votre p-valeur est très petite. Est-ce que ça veut dire que le gain est important ? »**

> Non. Une p-valeur dit que l'écart est difficilement attribuable au hasard, pas qu'il est
> grand. Sur mille tirages, un écart minuscule peut sortir très significatif. C'est pour ça que
> nous donnons aussi la taille de l'effet, en pourcentage de coût.

**« Pourquoi mille tirages et pas cent, ou dix mille ? »**

> L'erreur d'estimation décroît comme un sur racine de N. Passer de cent à mille divise l'erreur
> par trois virgule deux, passer de mille à dix mille ne la divise que par trois virgule deux
> encore, pour dix fois plus de temps de calcul. Mille est le point où le gain de précision
> cesse de payer son coût. Et nous vérifions empiriquement cette décroissance aux trois échelles.

---

## 5. Les questions sur l'optimisation

**« Écrivez-moi votre fonction de coût et dérivez-la. »**

C'est la question la plus probable de toute la soutenance. La dérivation complète, en cinq
étapes, est dans [04_maths_optimisation.md](04_maths_optimisation.md), section 6. À savoir
refaire sans notes.

**« D'où sort la transposée ? »**

> Du calcul, pas d'une convention. Quand on dérive le terme de pénalité par rapport à un débit
> donné, on obtient une somme sur toutes les lignes de A, pondérée par les coefficients de la
> colonne correspondante. Sommer sur les lignes en parcourant une colonne, c'est exactement
> multiplier par A transposée.

**« Pourquoi votre fonction est-elle convexe ? »**

> Le terme de coût s'écrit `qᵀCq` avec C diagonale à coefficients strictement positifs, donc
> définie positive, donc strictement convexe. Le terme de pénalité est un carré, donc convexe
> pour tout µ positif. Une somme de fonctions convexes est convexe. L'hypothèse qui porte tout,
> c'est la stricte positivité des coûts, et c'est pour ça que nous la vérifions dans le code.

**« Pourquoi pénaliser au lieu d'utiliser les multiplicateurs de Lagrange ? »**

> Le sujet l'interdit explicitement, contrainte méthodologique 2. La raison affichée est de
> rester dans le cadre de la descente de gradient vue en cours. Avec Lagrange, la contrainte
> serait satisfaite exactement au lieu d'approximativement, mais il faudrait résoudre un système
> qui sort du programme.

Ne pas prétendre que la pénalisation est meilleure. Elle est imposée, et elle approche.

**« Pourquoi ne mettez-vous pas simplement µ très grand ? »**

> Parce que ça dégrade le conditionnement. Augmenter µ augmente la plus grande valeur propre de
> la hessienne, ce qui impose un pas plus petit via la borne, ce qui ralentit la convergence.
> Les deux effets sortent de la même matrice, donc ils vont toujours ensemble. C'est exactement
> le compromis que mesure notre Expérience 3, avec µ à un, dix, cent et mille.

**« Montrez-moi que max de q et zéro est bien une projection. »**

> On cherche le point le plus proche de q dans le domaine des débits positifs, donc le y positif
> qui minimise la somme des carrés des écarts. Cette somme se sépare composante par composante,
> et chaque sous-problème s'écrit : minimiser le carré de y moins q avec y positif. Si q est
> positif, le minimum est en q. Si q est négatif, la fonction est croissante sur les y positifs
> donc le minimum est en zéro. Dans les deux cas, c'est le maximum de q et de zéro.
>
> Ce qui rend cette projection aussi simple, c'est que le domaine ne couple pas les composantes.
> Elle ne le serait plus si on activait les contraintes de capacité.

**« Pourquoi la borne deux sur L ? »**

> L est la plus grande valeur propre de la hessienne, c'est-à-dire la raideur maximale de la
> fonction. Si le pas dépasse deux sur L, un pas de descente saute par-dessus le fond et
> remonte plus haut qu'il n'était parti, et ça diverge. Nous le vérifions empiriquement dans
> l'Expérience 4, avec des pas de part et d'autre du seuil.

**« Comment savez-vous que vous avez convergé ? »**

Autre question qui distingue.

> Pas sur la norme du gradient. À l'optimum, certaines conduites ont un débit nul, coincé contre
> la frontière, et pour ces composantes le gradient pousse encore vers l'extérieur du domaine.
> La projection l'annule à chaque itération, donc le gradient ne tend pas vers zéro. Le bon
> critère porte sur le déplacement : on s'arrête quand q ne bouge plus, ce qui capte le point
> fixe de l'itération projetée.

**« Votre courbe descend. C'est une preuve de convergence ? »**

> Non, c'est une illustration. La preuve, c'est le lien entre la constante de Lipschitz calculée
> à partir de la matrice et le comportement observé de part et d'autre du seuil. C'est pour ça
> que nous lançons aussi des pas au-delà de la borne, pour montrer que ça diverge là où la
> théorie annonce que ça doit diverger.

---

## 6. Les questions sur le code et la validation

**« Comment savez-vous que votre gradient est juste ? »**

> Par différences finies centrées. On compare le gradient analytique au gradient estimé
> numériquement en bougeant une composante de un millionième. La différence centrée plutôt que
> décentrée, parce que son erreur décroît en h carré au lieu de h, ce qui permet de distinguer
> une vraie erreur de dérivation du bruit d'arrondi. Un écart relatif au-dessus de un millionième
> signale un problème.
>
> Cette vérification ne remplace pas la dérivation à la main, elle la contrôle.

**« Avez-vous testé votre solveur sur un cas dont vous connaissez la réponse ? »**

> Oui. Un réservoir, un quartier, deux conduites parallèles de coûts un et trois, une demande de
> cent. La solution se pose à la main : les débits se répartissent en proportion inverse des
> coûts, donc soixante-quinze et vingt-cinq. Ce cas prend en défaut une erreur de signe, un
> facteur deux oublié et une transposée manquante.

**« Vos résultats sont-ils reproductibles ? »**

> Oui, la graine du générateur aléatoire est fixée à quarante-deux dans la configuration, et
> nous passons un générateur explicite plutôt que d'utiliser l'état global de NumPy. En relançant
> le code, vous obtenez exactement les chiffres du rapport.

**« Avez-vous utilisé scipy.optimize ? »**

> Non, c'est interdit par le sujet. La descente de gradient projetée est écrite à la main, à
> partir de notre propre dérivation. Scipy ne sert qu'à l'algèbre linéaire et aux lois de
> probabilité.

---

## 7. Les questions sur les limites, et pourquoi il vaut mieux les amener soi-même

Un jury qui trouve une faiblesse que le groupe n'a pas vue enlève des points. Un jury à qui le
groupe présente la faiblesse en connaissance de cause en donne. La section « Limites » du
rapport est notée.

**« Votre objectif ne contient aucun terme d'équité. Comment pouvez-vous parler de
répartition équitable ? »**

C'est la meilleure question du sujet, et il faut l'attendre.

> Vous avez raison, il n'y en a pas. L'équité que nous observons est un effet indirect du coût
> quadratique, qui pousse à étaler les débits plutôt qu'à les concentrer, parce que doubler un
> débit quadruple son coût. Nous la mesurons a posteriori, avec l'écart-type des taux de
> satisfaction et le taux du quartier le moins bien servi, mais nous ne l'avons pas optimisée.
> Ajouter un terme d'équité explicite serait la première amélioration du modèle.

**« Vos capacités de conduites ne sont pas respectées. »**

> Le modèle n'impose que la positivité, pas les capacités. Les capacités du fichier de
> configuration sont descriptives. Nous vérifions a posteriori si la solution les dépasse, et
> nous le signalons. Les imposer demanderait un second terme de pénalisation, ce qui est une
> extension naturelle mais qui sort du périmètre.

**« Votre réseau est inventé. »**

> Le sujet ne demande pas de données réelles, et le plan recommande explicitement un jeu
> synthétique à condition de défendre sa construction. Nous justifions le nombre de quartiers,
> l'ordre de grandeur des demandes, le coefficient de variation entre douze et vingt-huit pour
> cent, et la corrélation modérée entre quartiers proches.

**« Que se passe-t-il si l'offre totale ne couvre pas la demande tirée ? »**

Question technique que peu de groupes auront préparée.

> La conservation `Aq = b` n'est exactement satisfiable que si l'offre couvre la demande. Sur un
> scénario tiré au hasard, la somme des demandes n'égale pas la somme des offres. Trois issues
> possibles : renormaliser l'offre, introduire un nœud de délestage, ou accepter une violation
> résiduelle qu'on mesure par la norme de `Aq` moins `b`. Nous avons retenu [à compléter par le
> groupe] et le rapport le justifie.

Cette réponse est à finaliser avec M1 et M4. Le point est signalé dans
`data/network_config.json`, dans la clé `_a_defendre_dans_le_rapport`.

---

## 8. Les questions personnelles

**« Quelle a été votre contribution exactement ? »**

Répondre par les livrables, pas par les intentions. Les modules codés, les six expériences
lancées, les figures produites, les tests écrits.

**« Qu'est-ce que vous n'avez pas compris tout de suite ? »**

Question fréquente et piégeuse par sa gentillesse. Une réponse honnête sur un point précis vaut
mieux qu'un « tout allait bien ». Le déficit de rang de A et le fait que ça crée un espace de
solutions est un bon candidat, parce que c'est la difficulté conceptuelle réelle du sujet et
que l'expliquer montre qu'on l'a franchie.

**« Si vous aviez trois semaines de plus ? »**

> Ajouter un terme d'équité explicite dans l'objectif et regarder comment il se comporte face
> au coût. Activer les contraintes de capacité par une seconde pénalisation. Et tester une loi
> de demande non gaussienne, log-normale par exemple, pour voir si les conclusions tiennent.

---

## 9. La checklist de la veille

- Savoir écrire la matrice d'incidence d'un réseau à trois nœuds au tableau.
- Savoir dériver `∇J` de zéro, sans notes, en moins de cinq minutes.
- Connaître par cœur : rang égale onze, noyau de dimension quatre, quinze conduites, douze
  nœuds, dix quartiers, deux réservoirs, mille tirages, graine quarante-deux.
- Savoir expliquer le conditionnement avec la vallée, sans écrire de formule.
- Savoir dire pourquoi le critère d'arrêt ne porte pas sur le gradient.
- Avoir sous la main les chiffres réels des six expériences, pas des ordres de grandeur.
- Avoir relu la section « Limites » du rapport, et pouvoir en citer trois sans réfléchir.
