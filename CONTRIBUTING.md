# Travailler à 6 sur ce dépôt

Six personnes touchent au même code sur trois semaines. Ces quelques règles existent pour
qu'on ne perde pas de temps en conflits et en versions divergentes.

## Branches

`main` reste toujours dans un état qui s'exécute. On n'y pousse jamais directement.

Chaque membre travaille sur une branche nommée d'après son périmètre :

```
m1-reseau          m2-algebre        m3-probabilites
m4-optimisation    m5-implementation m6-validation
```

Pour une tâche ponctuelle hors de son périmètre : `m3-correction-ic`, `m5-fix-projection`.

## Cycle de travail

```bash
git checkout main
git pull
git checkout -b m2-algebre
# ... travail ...
git add <fichiers précis, pas git add .>
git commit -m "Construit la matrice d'incidence et calcule son rang"
git push -u origin m2-algebre
```

Puis une pull request sur GitHub, relue par au moins **une autre personne** avant fusion.

## Messages de commit

À l'infinitif ou à la troisième personne du présent, en français, une ligne, ce que fait le
commit et non ce qu'on a touché :

- `Dérive le gradient du terme de pénalisation et le vérifie par différences finies`
- `update objective.py`
- `fix`

Si le commit demande une explication, elle va dans le corps du message, après une ligne
vide — pas dans un commentaire de code.

## La règle qui prime sur toutes les autres

**Aucune formule n'est codée avant d'avoir été dérivée à la main dans le rapport et relue.**

Concrètement, une pull request qui implémente `∇J(q)` doit pointer, dans sa description,
vers la section du rapport où la dérivation figure. Sans cette référence, elle n'est pas
fusionnée. C'est la Contrainte méthodologique 1 du sujet, et elle est notée.

Les modules de `src/optimization/` restent à l'état de squelette tant que les huit points du
jalon de passage (section 16 du plan, repris dans le README) ne sont pas cochés.

## Ce qui ne se versionne pas

`results/figures/` et `results/tables/` sont régénérables : on versionne le script qui les
produit, pas sa sortie. Exception au moment de la remise — les figures effectivement citées
dans le rapport doivent être ajoutées avec `git add -f`, sinon le rapport final renvoie à
des fichiers absents du dépôt.

Les notebooks de `notebooks/` servent à explorer. Rien de ce qui compte pour la note ne
doit exister uniquement dans un notebook : dès qu'un bout de code fonctionne, il migre dans
`src/`.

## Relecture croisée

Le sujet impose que certains éléments soient relus par quelqu'un d'autre que leur auteur.
On applique la même règle au code :

| Élément | Relu par |
|---|---|
| Dérivation de `∇J(q)` | deux membres autres que M4 |
| Matrice `A` et son rang | M1 (interprétation physique) |
| Modèle de demande | M6 |
| Chaque case de la checklist finale | une personne autre que le producteur |
