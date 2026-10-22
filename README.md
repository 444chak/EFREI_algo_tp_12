# TP - Optimisation d'un système de préparation de livraisons

## Langage : Python

J'ai choisi Python pour trois raisons :

- c'est le langage avec lequel je suis le plus à l'aise, et celui que j'ai toujours utilisé pour écrire des algorithmes
- sa syntaxe est concise, ce qui rend les algorithmes plus lisibles : le code reste proche de l'idée de l'algorithme
- la mémoire est gérée automatiquement (pas de `malloc`/`free`), ce qui me permet de me concentrer sur les choix algorithmiques plutôt que sur la gestion des pointeurs et des allocations.

Version utilisée : Python 3.14 (venv).

## Structure du projet

```text
src/
├── colis.py     # structure d'un colis
├── tri.py       # tri fusion
├── gestion.py   # collection de colis (ajout, recherche, affichage, tris, statistiques)
├── camion.py    # chargement du camion (programmation dynamique, glouton, score de priorité)
├── recherche.py # recherche linéaire et dichotomique (pour comparer avec le dictionnaire)
├── perf.py      # mesures de temps
├── tests.py     # tests
├── main.py      # interface web (Flask)
└── templates/
    └── index.html
```

## Lancer le programme

Installer Flask (une seule fois) :

```text
pip install -r requirements.txt
```

Puis, depuis `src/` :

```text
python main.py     # interface web sur http://localhost:8080
python tests.py    # tests
python perf.py     # mesures de temps
```

## Interface

Plutôt qu'un menu dans le terminal, j'ai fait une petite interface web avec Flask. Flask sert seulement à afficher la page et à recevoir les actions, tous les algorithmes restent dans mes fichiers Python. La page permet de :

- afficher les colis, triés par ordre d'ajout, poids, valeur ou priorité, dans les deux sens (seulement les 100 premiers pour ne pas surcharger la page avec 100 000 colis)
- ajouter un colis (l'ID doit être unique, le poids au moins 1 kg et la priorité au moins 1)
- rechercher un colis par son ID
- générer autant de colis aléatoires qu'on veut pour tester avec beaucoup de données
- charger les 5 colis de l'exemple de l'énoncé, ou tout réinitialiser pour repartir de 0 colis
- préparer un camion avec ou sans priorités, et voir le chargement avec le poids utilisé, la valeur, le score, le temps de calcul et ce qu'aurait donné le glouton
- voir les statistiques : nombre de colis, totaux, moyennes, répartition par destination et par priorité
- lancer les tests et voir le résultat de chacun
- lancer les mesures de performances (recherche, tri, camion quand n varie, camion quand C varie) et voir les tableaux de résultats

Les tests et les mesures peuvent aussi se lancer dans le terminal avec `python tests.py` et `python perf.py`.

Au démarrage, il n'y a aucun colis. Pour éviter de saturer la mémoire, la préparation du camion est refusée si le tableau de la DP dépasse 200 Mo (`n*C` octets).

## Rapport

Les choix algorithmiques, les complexités, les mesures de performances et les réponses aux questions sont dans [`rapport.md`](rapport.md) (et [`rapport.pdf`](rapport.pdf)).
