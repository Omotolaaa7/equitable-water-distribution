# Le prompt, réécrit

Le prompt de départ disait, en substance : « je prends les tâches du membre 5, je ne comprends
pas grand-chose, produis-moi de quoi comprendre tout le projet comme si j'étais débutante en
maths, pour pouvoir le présenter à n'importe qui ».

L'intention est bonne. Ce qui lui manquait, c'est le contexte qu'un modèle ne peut pas deviner
et les critères qui permettent de juger si le résultat est réussi. Voici la version à réutiliser.

---

## Version réutilisable

> **Contexte.**
> Je fais partie du Groupe 1 de l'Académie des Mathématiques Appliquées, superviseur
> Ir. Charbel Mamlankou. Notre sujet est le Thème 3 : répartir l'eau équitablement dans un
> quartier quand la demande est incertaine. Le dépôt de code est
> `Omotolaaa7/equitable-water-distribution`, et il contient déjà l'énoncé officiel
> (`docs/sujets_ama.pdf`) et le plan de projet du groupe
> (`docs/plan_projet_theme3_groupe1.pdf`). Lis ces deux documents avant de répondre.
>
> **Mon rôle.**
> J'assure les tâches du Membre 5 : implémenter `monte_carlo.py`, coder `objective.py` et
> `gradient_descent.py` à partir des dérivations du Membre 4, exécuter les 6 expériences,
> produire les figures et les tableaux. Je dépends du Membre 3 pour le modèle de demande et
> du Membre 4 pour les dérivations validées.
>
> **Mon niveau réel.**
> Je suis débutante en mathématiques. Je ne sais pas lire une formule matricielle sans aide.
> Les symboles Σ, ∇, ‖·‖, ᵀ, argmin ne me parlent pas encore. Ne suppose aucun prérequis
> au-delà du programme de terminale.
>
> **Ce que je veux obtenir.**
> Comprendre le projet entier, pas seulement ma partie, au point de pouvoir le présenter
> seule devant un jury et répondre à des questions que je n'aurai pas préparées. Je dois
> pouvoir expliquer chaque étape à quelqu'un qui n'y connaît rien, et justifier chaque choix
> de méthode auprès de quelqu'un qui s'y connaît.
>
> **Ce que le résultat doit contenir.**
> 1. Le projet raconté de bout en bout sans une seule formule, pour tenir la logique d'ensemble.
> 2. Chaque notion mathématique du sujet expliquée depuis zéro, dans l'ordre où le projet
>    s'en sert, avec à chaque fois : ce que c'est, à quoi ça sert ici, ce qui se passerait si
>    on s'en passait.
> 3. La dérivation complète du gradient, faite pas à pas, sans étape sautée.
> 4. Ma feuille de route de Membre 5 : quoi coder, dans quel ordre, ce qui me bloque et qui
>    me débloque.
> 5. Une préparation à la soutenance : les questions probables du jury avec leur réponse,
>    y compris les questions pièges et les faiblesses connues du projet.
> 6. Un glossaire de tous les symboles et termes, consultable pendant que je révise.
>
> **Contraintes de forme.**
> En français. Aucun tiret cadratin. Chaque terme technique suivi d'une explication de trois
> à six mots entre parenthèses, en langage courant, sans jamais sacrifier l'exactitude.
> Pas de tournure « ce n'est pas X, c'est Y ». Pas de conclusion qui résume le texte.
> Des chiffres nets plutôt que des fourchettes. Des fichiers Markdown déposés dans
> `docs/comprendre/` du dépôt, pour que le reste du groupe puisse s'en servir.
>
> **Critères de réussite.**
> Je dois pouvoir, après lecture : expliquer pourquoi `Aq = b` a plusieurs solutions et
> pourquoi c'est ce qui rend l'optimisation possible ; redériver `∇J(q)` sur une feuille
> sans regarder ; dire pourquoi on pénalise au lieu d'utiliser les multiplicateurs de
> Lagrange ; expliquer ce que veut dire un mauvais conditionnement à quelqu'un qui n'a
> jamais entendu le mot ; justifier le nombre de tirages Monte-Carlo choisi.
>
> **Ce que tu ne dois pas faire.**
> N'implémente pas les modules de `src/optimization/`. Le plan de projet pose un jalon
> bloquant en section 16 : aucune ligne de code d'optimisation avant que les dérivations
> soient écrites à la main et relues. Explique-moi le code que j'aurai à écrire, ne l'écris
> pas à ma place.

---

## Ce qui a changé, et pourquoi

| Ajout | Ce que ça débloque |
|---|---|
| Le sujet, le groupe, le superviseur, le dépôt | Sans ça, le modèle produit un cours générique sur les réseaux de flots, hors sujet |
| Les deux PDF cités par leur chemin | Le modèle lit l'énoncé réel au lieu de reconstituer un sujet plausible |
| Le rôle M5 et ses dépendances | Oriente la feuille de route vers ce qui me bloque vraiment |
| « Je ne sais pas lire une formule matricielle » | Fixe le plancher. Sans plancher explicite, le modèle vise le niveau moyen d'un étudiant en L3 |
| Les six éléments attendus, numérotés | Rend le résultat vérifiable point par point |
| Les critères de réussite formulés en actions | « Je dois pouvoir redériver ∇J sans regarder » est testable, « je veux bien comprendre » ne l'est pas |
| L'interdiction de coder `src/optimization/` | Empêche de violer la contrainte méthodologique qui est notée |

Le point qui compte le plus, à mon avis, c'est la section « critères de réussite ». Un prompt
qui décrit ce que le lecteur doit savoir faire après lecture produit un document utilisable.
Un prompt qui décrit un sujet produit un exposé.

## Pour réutiliser ce prompt sur autre chose

La structure tient en sept blocs : contexte, rôle, niveau réel, objectif, contenu attendu
numéroté, contraintes de forme, critères de réussite mesurables. Le huitième bloc, ce qu'il
ne faut pas faire, sert quand il existe une règle du jeu qu'un modèle ignorerait
spontanément. Ici c'est le jalon de la section 16.
