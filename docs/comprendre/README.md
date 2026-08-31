# Comprendre le projet de bout en bout

Dossier de travail écrit pour quelqu'un qui débute en mathématiques et qui doit pouvoir
présenter le projet entier, pas seulement sa partie. Aucun prérequis au-delà du programme de
terminale.

Utile au groupe entier, pas seulement au Membre 5.

---

## État des chiffres, au 30 août 2026

Les chiffres de ce dossier ont été repris après que le Membre 1 a figé la topologie définitive.
Le réseau compte désormais 2 réservoirs, 8 quartiers et 13 conduites, contre 12 nœuds et 15
conduites dans le gabarit de départ. Le rang de `A` vaut 9, le noyau reste de dimension 4, et
le quartier fragile est Q1 et non plus Q10.

Toutes les valeurs citées ici ont été recalculées en exécutant le code fusionné sur
`data/network_config.json`. Si M1 modifie à nouveau la topologie, il faut refaire ce passage.

Le 31 août, le modèle de demande a été branché sur `network_config.json`, ce qui a supprimé
l'écart de corrélations entre le fichier du Membre 1 et le code du Membre 3. Sept tests le
vérifient désormais paire par paire.

Un point reste ouvert et il est signalé dans les documents concernés :
`experiments/exp6_at_risk_districts.py` ne s'exécute pas en ligne de commande.

## Dans quel ordre lire

| Ordre | Document | Durée | Quand |
|---|---|---|---|
| 1 | [01_le_projet_sans_maths.md](01_le_projet_sans_maths.md) | 20 min | Tout de suite, et la veille de la soutenance |
| 2 | [08_ce_qui_existe_deja.md](08_ce_qui_existe_deja.md) | 25 min | Juste après, pour voir ce qui est déjà construit |
| 3 | [02_maths_graphe_et_algebre.md](02_maths_graphe_et_algebre.md) | 45 min | Avant de toucher à `src/graph/` |
| 4 | [03_maths_probabilites_et_statistiques.md](03_maths_probabilites_et_statistiques.md) | 45 min | Avant de coder `monte_carlo.py` |
| 5 | [04_maths_optimisation.md](04_maths_optimisation.md) | 1 h | Avant de coder `objective.py`. Le plus important |
| 6 | [05_role_membre_5.md](05_role_membre_5.md) | 20 min | Pour savoir par quoi commencer dès aujourd'hui |
| 7 | [06_soutenance_questions_reponses.md](06_soutenance_questions_reponses.md) | 40 min | À réviser une semaine avant la soutenance |
| 8 | [07_glossaire.md](07_glossaire.md) | consultation | À garder ouvert pendant toute la lecture |

Le document [00_prompt_optimise.md](00_prompt_optimise.md) contient le prompt qui a servi à
produire ce dossier, et une explication de ce qui a été ajouté au prompt de départ. Il sert de
gabarit réutilisable pour d'autres demandes.

## Si vous n'avez qu'une heure

Lire le 01 en entier, puis la section 6 du 04, celle qui dérive le gradient pas à pas. Ce sont
les deux morceaux qui portent le plus de compréhension par minute de lecture.

## Si vous n'avez que dix minutes avant la soutenance

La section 1 du 06, les trois versions de la présentation. Et les chiffres de la section 3 du
07.

## La phrase à retenir si vous n'en retenez qu'une

Le réseau contient des boucles. Une boucle crée plusieurs façons d'acheminer la même eau au
même quartier. La conservation des flux ne suffit donc pas à décider, elle laisse un espace de
solutions de dimension 4. C'est ce choix résiduel que l'optimisation tranche, en retenant la
répartition la moins chère.

Sans cycle, pas de choix. Sans choix, pas d'optimisation. Sans optimisation, pas de projet.

## Sources

Tout ce dossier découle de deux documents, à lire aussi dans leur version d'origine :

- [docs/sujets_ama.pdf](../sujets_ama.pdf), l'énoncé officiel des quatre thèmes, 7 pages
- [docs/plan_projet_theme3_groupe1.pdf](../plan_projet_theme3_groupe1.pdf), le plan de projet du
  groupe, 34 pages

Quand ce dossier et l'énoncé se contredisent, c'est l'énoncé qui fait foi.
