# Fly-in
Les drones, c’est intéressant.

Résumé : Concevoir un système efficace de routage de drones qui navigue entre plusieurs drones à travers des zones connectées tout en minimisant le nombre de tours de simulation et en gérant les contraintes de mouvement.

Version : 1.6

## Table des matières
I Avant-propos 2
II Instructions relatives à l’IA 3
III Consignes communes 5
III.1 Règles générales 5
III.2 Makefile 5
III.3 Consignes complémentaires 6
IV Introduction 7
V Contraintes 8
VI Laissez le drone voler 9
VII Partie obligatoire 11
VII.1 Recherche de chemin et exigences algorithmiques 11
VII.2 Règles d’occupation des zones 12
VII.3 Mécanismes de déplacement et de tour 12
VII.4 Contraintes du parseur 13
VII.5 Format de sortie de la simulation 15
VII.6 Système de score 15
VII.7 Références de performance 17
VIII Exigences du README 20
IX Partie bonus 21
X Soumission et évaluation par les pairs 22

1

## Chapitre I
### Avant-propos

Les drones ont été utilisés pour rassembler des moutons en Nouvelle-Zélande, remplaçant les bergers par des pâtres aériens bourdonnants. Au Japon, certains bâtiments de bureaux déploient des drones qui diffusent de la musique forte et font clignoter des lumières pour littéralement chasser les employés surmenés à la maison. Un drone a été entraîné à peindre des graffitis sur les murs en plein vol — un mélange rebelle de technologie et d’art urbain. En Suède, des scientifiques ont utilisé des drones pour repérer des excréments de baleines flottant à la surface de l’océan afin d’étudier des espèces menacées. Certains drones expérimentaux ont la forme d’oiseaux ou d’insectes pour espionner sans être remarqués, avec des ailes qui battent. Il existe même un drone qui vole en faisant flotter des bulles de savon, sans hélices. Dans le cadre de la recherche sur les volcans, un drone a déjà volé droit dans un nuage d’éruption, s’est fondu en plein air, mais a réussi à renvoyer des données quelques secondes avant sa désintégration. En Corée du Sud, des spectacles synchronisés de drones ont remplacé les feux d’artifice — plus sûrs, silencieux et d’une beauté presque magique.

L’expression vient de l’idée que la roue est une invention brillante qui existe depuis toujours et qui fonctionne très bien. Comme il n’y a rien de mal à cela, essayer de l’inventer à nouveau ne servirait pas à grand-chose et pourrait être une perte de temps — surtout si ce temps pouvait être utilisé pour résoudre de nouveaux problèmes.

En programmation, cela se produit lorsqu’une personne construit quelque chose à partir de zéro alors qu’un équivalent existe déjà — par exemple, écrire son propre algorithme de tri ou sa propre bibliothèque quand des versions solides et open-source existent déjà. Mais ce n’est pas entièrement négatif : le faire soi-même peut être un excellent moyen d’apprendre à comprendre le fonctionnement interne des outils. La clé est de trouver un équilibre — ne pas reconstruire tout, mais prendre le temps d’explorer comment fonctionnent réellement les outils que vous utilisez. De cette façon, vous progresserez en tant que développeur sans vous enliser à réinventer les mêmes roues.

2

## Chapitre II
### Instructions relatives à l’IA

- Contexte

Au cours de votre apprentissage, l’IA peut vous aider à accomplir de nombreuses tâches. Prenez le temps d’explorer les différentes capacités des outils d’IA et la façon dont ils peuvent soutenir votre travail. Cependant, abordez-les avec prudence et évaluez de manière critique les résultats. Que ce soit pour du code, de la documentation, des idées ou des explications techniques, vous ne pouvez jamais être totalement certain que votre question a été formulée de manière adéquate ou que le contenu généré est exact. Vos pairs constituent une ressource précieuse pour vous aider à éviter les erreurs et les angles morts.

- Message principal

☛ Utilisez l’IA pour réduire les tâches répétitives ou fastidieuses.

☛ Développez des compétences de formulation de requêtes — aussi bien en codage que hors codage — qui seront utiles pour votre avenir professionnel.

☛ Apprenez le fonctionnement des systèmes d’IA afin de mieux anticiper et éviter les risques, biais et enjeux éthiques fréquents.

☛ Continuez à développer vos compétences techniques et humaines en travaillant avec vos pairs.

☛ N’utilisez du contenu généré par l’IA que si vous le comprenez parfaitement et pouvez en assumer la responsabilité.

- Règles de l’apprenant :

• Prenez le temps d’explorer les outils d’IA et de comprendre leur fonctionnement, afin de pouvoir les utiliser de manière éthique et réduire les biais potentiels.
• Réfléchissez à votre problème avant de faire une requête — cela vous aide à rédiger des prompts plus clairs, plus détaillés et plus pertinents, en utilisant un vocabulaire précis.
• Développez l’habitude de vérifier, revoir, questionner et tester systématiquement tout contenu généré par l’IA.
• Recherchez toujours une relecture par les pairs — ne vous fiez pas uniquement à votre propre validation.

3

Fly-in Les drones, c’est intéressant.

- Résultats attendus :

• Développez des compétences de prompting à la fois générales et spécifiques à un domaine.
• Améliorez votre productivité grâce à une utilisation efficace des outils d’IA.
• Continuez à renforcer votre pensée computationnelle, votre résolution de problèmes, votre adaptabilité et votre collaboration.

- Commentaires et exemples :

• Vous rencontrerez régulièrement des situations — examens, évaluations, etc. — où vous devrez démontrer une vraie compréhension. Préparez-vous et continuez à développer vos compétences techniques et relationnelles.
• Expliquer votre raisonnement et débattre avec vos pairs révèle souvent des lacunes dans votre compréhension. Faites de l’apprentissage entre pairs une priorité.
• Les outils d’IA manquent souvent de votre contexte spécifique et tendent à fournir des réponses génériques. Vos pairs, qui partagent votre environnement, peuvent offrir des perspectives plus pertinentes et plus précises.
• Là où l’IA a tendance à générer la réponse la plus probable, vos pairs peuvent proposer des perspectives alternatives et des nuances précieuses. Faites d’eux un point de contrôle qualité.

✓ Bonne pratique :

Je demande à l’IA : « Comment tester une fonction de tri ? » Elle me donne quelques idées. Je les teste et je les passe en revue avec un pair. Nous affinons l’approche ensemble.

✗ Mauvaise pratique :

Je demande à l’IA d’écrire une fonction entière, je la copie-collé dans mon projet. Lors de l’évaluation par les pairs, je ne peux pas expliquer ce qu’elle fait ni pourquoi. Je perds en crédibilité — et je rate mon projet.

✓ Bonne pratique :

J’utilise l’IA pour aider à concevoir un parseur. Puis je parcours la logique avec un pair. Nous repérons deux bugs et les réécrivons ensemble — mieux, plus propre et entièrement compris.

✗ Mauvaise pratique :

Je laisse Copilot générer du code pour une partie essentielle de mon projet. Cela compile, mais je ne peux pas expliquer comment il gère les tuyaux. Pendant l’évaluation, je ne parviens pas à justifier et je rate mon projet.

4

## Chapitre III
### Consignes communes

#### III.1 Règles générales

• Votre projet doit être écrit en Python 3.10 ou plus récent.
• Votre projet doit respecter les standards de codage flake8.
• Vos fonctions doivent gérer les exceptions proprement pour éviter les crashes. Utilisez des blocs try/except pour gérer les erreurs potentielles. Préférez les gestionnaires de contexte pour les ressources comme les fichiers ou les connexions afin d’assurer un nettoyage automatique. Si votre programme plante à cause d’exceptions non gérées pendant la revue, il sera considéré comme non fonctionnel.
• Toutes les ressources (par ex. des poignées de fichiers, des connexions réseau) doivent être correctement gérées pour éviter les fuites. Utilisez des context managers lorsque c’est possible pour une gestion automatique.
• Votre code doit inclure des annotations de type pour les paramètres de fonctions, les types de retour et les variables lorsque c’est applicable (en utilisant le module typing). Utilisez mypy pour la vérification statique des types. Toutes les fonctions doivent passer mypy sans erreur.
• Incluez des docstrings dans les fonctions et classes suivant PEP 257 (par exemple style Google ou NumPy) pour documenter l’objectif, les paramètres et les retours.

#### III.2 Makefile

Incluez un Makefile dans votre projet pour automatiser les tâches courantes. Il doit contenir les règles suivantes (lint obligatoire implique les drapeaux spécifiés ; il est fortement recommandé d’essayer --strict pour un contrôle renforcé) :

• install : installer les dépendances du projet avec pip, uv, pipx ou tout autre gestionnaire de paquets de votre choix.
• run : exécuter le script principal du projet (par exemple via l’interpréteur Python).
• debug : exécuter le script principal en mode débogage avec le debugger intégré de Python (par exemple pdb).
• clean : supprimer les fichiers temporaires ou caches (par ex. __pycache__, .mypy_cache) pour garder l’environnement propre.
• lint : exécuter les commandes flake8 . et mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
• lint-strict (optionnel) : exécuter les commandes flake8 . et mypy . --strict

#### III.3 Consignes complémentaires

• Créez des programmes de test afin de vérifier le fonctionnement du projet (non soumis ni notés). Utilisez des frameworks comme pytest ou unittest pour des tests unitaires couvrant les cas limites.
• Incluez un fichier .gitignore pour exclure les artefacts Python.
• Il est recommandé d’utiliser des environnements virtuels (par ex. venv ou conda) pour isoler les dépendances pendant le développement.

Si des exigences supplémentaires propres au projet s’appliquent, elles seront indiquées immédiatement sous cette section.

5

## Chapitre IV
### Introduction

Les drones autonomes sont l’avenir du transport. Ils sont déjà utilisés dans de nombreuses industries, comme l’agriculture, la construction et la logistique. Ils sont aussi utilisés dans des opérations militaires, comme la surveillance et la reconnaissance.

Votre mission est de concevoir un système qui route efficacement une flotte de drones depuis une base centrale (départ) vers un emplacement cible (arrivée), tout en naviguant dans ce réseau dynamique sous un ensemble de contraintes strictes et d’objectifs d’optimisation.

Vous recevrez un graphe représentant le réseau de zones, ainsi qu’un ensemble de contraintes à respecter.

Le graphe est représenté comme un réseau de zones connectées, où les connexions définissent les chemins de déplacement possibles entre les zones.

6

## Chapitre V
### Contraintes

• Toute bibliothèque facilitant la logique de graphe est interdite (comme networkx, graphlib, etc.).
• Le projet doit être complètement typesafe. L’utilisation de flake8 et mypy est obligatoire.
• Le projet doit être entièrement orienté objet.

Cela devra être démontré pendant la revue par les pairs.

7

## Chapitre VI
### Laissez le drone voler

Joint à ce sujet, vous trouverez plusieurs fichiers représentant le réseau de zones au format suivant :

Exemple :

```text
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green capacity=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [capacity=2]
connection: tunnelB-goal
```

C’est intéressant, n’est-ce pas ? Pour être plus précis :

• La première ligne définit le nombre de drones avec `nb_drones: <number>`.
• La définition des zones sur chaque ligne utilise des préfixes de type :
  ◦ `start_hub: <name> <x> <y> [metadata]` marque la zone de départ.
  ◦ `end_hub: <name> <x> <y> [metadata]` marque la zone d’arrivée.
  ◦ `hub: <name> <x> <y> [metadata]` définit une zone régulière.
  ◦ La syntaxe des connexions interdit les tirets dans les noms de zones (voir ci-dessous).
• Tous les métadonnées sont optionnels et placés entre crochets `[...]` avec des valeurs par défaut :
  ◦ `zone=<type>` (par défaut : normal)
  ◦ `color=<value>` (par défaut : none)
  ◦ `capacity=<number>` (par défaut : 1) — nombre maximal de drones pouvant occuper simultanément cette zone
  ◦ Les tags à l’intérieur des crochets peuvent apparaître dans n’importe quel ordre.

- Types de zone :
  ◦ normal — zone standard avec un coût de mouvement de 1 tour (par défaut)
  ◦ blocked — zone inaccessible. Les drones ne doivent ni entrer ni traverser cette zone. Tout chemin l’utilisant est invalide.
  ◦ restricted — zone sensible ou dangereuse. Le mouvement vers cette zone coûte 2 tours.
  ◦ priority — zone privilégiée. Le mouvement vers cette zone coûte 1 tour mais doit être prioritaire dans la recherche de chemin.

- Couleurs :
  ◦ Les couleurs sont optionnelles et peuvent servir à la représentation visuelle (sortie terminale ou affichage graphique).
  ◦ Les valeurs acceptées pour la couleur sont n’importe quelle chaîne valide d’un seul mot (par ex. red, blue, gray). Il n’existe pas de liste fixe de couleurs autorisées.
  ◦ Lorsque des couleurs sont spécifiées, l’implémentation doit fournir un retour visuel via une sortie terminale colorée ou une représentation graphique.

- Les connexions sont définies avec la syntaxe `connection: <name1>-<name2> [metadata]` :
  ◦ Elles définissent une connexion bidirectionnelle (arête) entre deux zones.
  ◦ La syntaxe des connexions interdit les tirets dans les noms de zones.
  ◦ Des métadonnées optionnelles peuvent être spécifiées entre crochets `[...]` :
    ∗ `capacity=<number>` (par défaut : 1) — nombre maximal de drones pouvant traverser cette connexion simultanément.

- Les commentaires commencent par `#` et sont ignorés.

Les coordonnées des zones seront toujours des entiers, et il existera toujours un départ unique et une arrivée unique.

8

## Chapitre VII
### Partie obligatoire

Comme vous l’avez deviné, l’objectif principal est de déplacer tous les drones depuis la zone de départ vers la zone d’arrivée en un minimum de tours de simulation.

#### VII.1 Recherche de chemin et exigences algorithmiques

• Les drones peuvent se déplacer simultanément. L’algorithme doit planifier des chemins pour maximiser le débit et éviter les délais inutiles.
• Votre implémentation doit gérer :
  ◦ la distribution des drones sur plusieurs chemins ;
  ◦ l’attente stratégique lorsque le mouvement n’est pas possible ;
  ◦ l’évitement des conflits de chemin et des interblocages.
• L’algorithme doit tenir compte :
  ◦ des longueurs de chemin, y compris les coûts de mouvement associés aux types de zones (par ex. restricted ou priority) ;
  ◦ de l’ordonnancement des tours pour éviter les collisions ou les blocages entre drones ;
  ◦ de la structure du graphe pour déterminer les chemins disjoints ou chevauchants disponibles ;
  ◦ des contraintes de capacité des zones (`capacity`) et des connexions (`capacity`).
• Votre algorithme doit être adaptable : différentes cartes peuvent nécessiter différentes stratégies de routage selon la topologie et les types de zones.
• Représentation visuelle : votre implémentation doit fournir un retour visuel de la simulation, soit par :
  ◦ une sortie terminale colorée montrant les mouvements des drones et l’état des zones ;
  ◦ une interface graphique affichant le réseau et les positions des drones ;
  ◦ les deux options pour une meilleure expérience utilisateur.

• À quel point votre algorithme est-il efficace ?
• Peut-il fonctionner avec un grand nombre de drones ?
• Quelle est sa complexité (par ex. O(n), O(log n), etc.) ?
• Recalculez-vous ou mettez-vous en cache les chemins ?
• Quel impact cela a-t-il sur l’usage mémoire ?
• Comment votre représentation visuelle améliore-t-elle la compréhension de la simulation ?

#### VII.2 Règles d’occupation des zones

• Par défaut, une zone ne peut contenir au plus qu’un drone à chaque tour de simulation.
• Les zones avec la métadonnée `capacity=N` peuvent contenir jusqu’à N drones simultanément.
• Les seules exceptions spéciales aux règles d’occupation sont :
  ◦ la zone de départ : tous les drones commencent ici et peuvent partager cet espace initialement ;
  ◦ la zone d’arrivée : plusieurs drones peuvent arriver ici et sont considérés comme livrés.
• Deux drones ne peuvent pas entrer dans la même zone au même tour, sauf si la capacité de la zone le permet.
• Un drone ne peut pas se déplacer vers une zone qui dépasserait sa capacité maximale.
• La capacité des connexions (`capacity`) définie sur les connexions limite le nombre de drones pouvant traverser la même connexion simultanément.
• Les drones peuvent se déplacer simultanément, tant que toutes les contraintes de capacité sont respectées.

#### VII.3 Mécanismes de déplacement et de tour

La simulation se déroule en tours discrets. À chaque tour, chaque drone peut :

• se déplacer vers une zone adjacente connectée (si la capacité le permet) ;
• se déplacer vers une connexion en direction d’une zone restricted (ce qui demande 2 tours pour l’atteindre). Dans ce cas, le drone DOIT atteindre sa destination au tour suivant. Il ne peut pas attendre plusieurs tours sur la connexion ;
• rester sur place (par exemple pour attendre, ou si le mouvement est bloqué).

La simulation doit empêcher les conflits et garantir une planification de mouvement valide basée sur l’évaluation d’état tour par tour :

• Les drones qui sortent d’une zone libèrent de la capacité pour ce même tour.
• Une zone doit avoir une capacité disponible pour qu’un drone puisse s’y déplacer (après que tous les drones partant aient libéré de l’espace).
• Pour les mouvements sur plusieurs tours (zones restricted), le drone occupe la connexion pendant le transit et DOIT arriver à destination après le nombre de tours spécifié. Il ne peut pas attendre sur la connexion pour une place libre dans la zone de destination.

Chaque mouvement entre zones a un coût en tours, basé sur le type de la zone de destination :

• normal : 1 tour (par défaut)
• restricted : 2 tours
• priority : 1 tour (mais doit être privilégiée dans les algorithmes de recherche de chemin)
• blocked : inaccessible — ne peut pas être atteinte

#### VII.4 Contraintes du parseur

Le fichier d’entrée doit respecter la structure et la syntaxe attendues :

• La première ligne doit définir le nombre de drones avec `nb_drones: <positive_integer>`.
• Le programme doit être capable de gérer n’importe quel nombre de drones.
• Il doit y avoir exactement un `start_hub:` et un `end_hub:`.
• Chaque zone doit avoir un nom unique et des coordonnées entières valides.
• Les noms de zones peuvent utiliser n’importe quel caractère valide sauf les tirets et les espaces.
• Les connexions doivent relier uniquement des zones déjà définies avec `connection: <zone1>-<zone2> [metadata]`.
• La même connexion ne doit pas apparaître plus d’une fois (par exemple `a-b` et `b-a` sont considérés comme dupliqués).
• Tout bloc de métadonnées (par ex. `[zone=... color=...]` pour les zones, `[capacity=...]` pour les connexions) doit être syntaxiquement valide.
• Les types de zone doivent être l’un des suivants : normal, blocked, restricted, priority. Tout type invalide doit déclencher une erreur de parsing.
• Les valeurs de capacité (`capacity` pour les zones, `capacity` pour les connexions) doivent être des entiers positifs.
• La capacité `capacity` est ignorée sur les zones `start_hub` et `end_hub` : elles n’ont pas de limite de capacité (tous les drones peuvent commencer dans la zone de départ, et n’importe quel nombre de drones peut être livré à la zone d’arrivée). Si de telles métadonnées sont présentes sur ces deux zones, elles sont ignorées et ne constituent pas une erreur de validation.
• Toute autre erreur de parsing doit arrêter le programme et renvoyer un message d’erreur clair indiquant la ligne et la cause.

Il est fortement recommandé de créer vos propres fichiers de carte à partir de ceux fournis dans le sujet pour gérer les cas limites et les erreurs.

#### VII.5 Format de sortie de la simulation

• La simulation doit afficher pas à pas les mouvements des drones depuis la zone de départ jusqu’à la zone d’arrivée.
• Chaque tour de simulation est représenté par une ligne.
• Une ligne doit lister tous les mouvements de drones qui ont lieu pendant ce tour, séparés par des espaces. Chaque mouvement doit suivre le format : `D<ID>-<zone>` ou `D<ID>-<connection>` si le drone est encore en vol vers une zone restricted.
  ◦ `D<ID>` désigne l’identifiant unique du drone (par ex. D1, D2).
  ◦ `<zone>` est le nom de la zone de destination.
  ◦ `<connection>` est le nom de la connexion vers une zone restricted.
• Les drones qui ne bougent pas à un tour donné sont omis de cette ligne.
• Les drones qui atteignent la zone d’arrivée sont considérés comme livrés et ne sont plus suivis.
• La simulation se termine lorsque tous les drones ont atteint la zone d’arrivée.
• Exemple :

```text
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

#### VII.6 Système de score

• La performance d’une solution est évaluée en fonction du nombre total de tours de simulation nécessaires pour acheminer tous les drones depuis la zone de départ vers la zone d’arrivée.
• Plus le nombre de tours est faible, meilleur est le score.
• Une simulation valide doit :
  ◦ respecter toutes les règles de mouvement et d’occupation ;
  ◦ gérer correctement les coûts de mouvement liés aux types de zones ;
  ◦ respecter toutes les contraintes de capacité (zones et connexions) ;
  ◦ éviter tous les conflits (par ex. dépasser la capacité d’une zone ou d’une connexion).

Des métriques secondaires optionnelles peuvent inclure :

• le nombre de drones déplacés par tour (efficacité de l’allocation des chemins) ;
• le nombre moyen de tours par drone ;
• le coût total du chemin (somme des coûts de mouvement pondérés sur tous les drones).

En cas de nombre de tours identiques, les solutions peuvent être comparées sur la base de métriques secondaires ou de la qualité du code.

Ces métriques secondaires ne sont pas obligatoires à calculer automatiquement, mais il est recommandé aux apprenants de les afficher dans leur sortie de simulation ou leur documentation pour aider les pairs à évaluer la performance.

#### VII.7 Références de performance

Les cibles de performance suivantes définissent le niveau d’optimisation attendu que votre implémentation doit atteindre.

• Performance attendue :
  ◦ Les cartes faciles doivent être résolues en moins de 10 tours.
  ◦ Les cartes moyennes doivent être résolues en 10 à 30 tours.
  ◦ Les cartes difficiles doivent être résolues en moins de 60 tours.
  ◦ La carte challenger (optionnelle) doit viser à battre le record de référence de 45 tours.

Ce niveau est purement optionnel et n’affecte pas votre note.

Pour vous aider à évaluer l’efficacité de votre algorithme, voici des cibles de performance basées sur les cartes de test fournies :

• Cartes faciles :
  ◦ Chemin linéaire avec 2 drones : cible ≤ 6 tours
  ◦ Fourche simple avec 4 drones : cible ≤ 8 tours
  ◦ Capacité de base avec 4 drones : cible ≤ 6 tours

• Cartes moyennes :
  ◦ Piège de fin de chemin avec 5 drones : cible ≤ 12 tours
  ◦ Boucle circulaire avec 6 drones : cible ≤ 15 tours
  ◦ Puzzle de priorité avec 5 drones : cible ≤ 12 tours

• Cartes difficiles :
  ◦ Maze nightmare avec 8 drones : cible ≤ 30 tours
  ◦ Capacity hell avec 12 drones : cible ≤ 35 tours
  ◦ Ultimate challenge avec 15 drones : cible ≤ 45 tours

• Carte challenger (optionnelle — pour les implémentations exceptionnelles) :
  ◦ The Impossible Dream avec 25 drones : record de référence : 45 tours
  ◦ Ce défi quasi insoluble est conçu pour la recherche et l’optimisation algorithmique.
  ◦ Résoudre cette carte démontre des compétences exceptionnelles en recherche de chemin et en optimisation.
  ◦ Note : ce niveau est purement optionnel et n’affecte pas votre note.

Ces benchmarks servent d’objectifs d’optimisation pour vous aider à évaluer la performance de votre algorithme. Les atteindre démontre une implémentation très bien optimisée et sera évaluée lors de la revue par les pairs.

• Votre algorithme peut-il atteindre ces références de performance ?
• Comment votre solution se compare-t-elle aux cibles de référence ?
• Quelles optimisations avez-vous mises en place pour obtenir de meilleures performances ?
• Pouvez-vous résoudre la carte challenger et battre le record de 45 tours ?

Figure VII.1 : Carte easy 2
Figure VII.2 : Carte medium 3
Figure VII.3 : Carte hard 2

8

## Chapitre VIII
### Exigences du README

Un fichier README.md doit être fourni à la racine de votre dépôt Git. Son rôle est de permettre à toute personne non familière avec le projet (pairs, personnel, recruteurs, etc.) de comprendre rapidement de quoi il s’agit, comment l’exécuter et où trouver plus d’informations sur le sujet.

Le README.md doit inclure au moins :

• La toute première ligne doit être en italique et lire : Cet projet a été créé dans le cadre du cursus 42 par <login1>[, <login2>[, <login3>[...]]].
• Une section « Description » qui présente clairement le projet, y compris son objectif et un bref aperçu.
• Une section « Instructions » contenant toute information utile concernant la compilation, l’installation et/ou l’exécution.
• Une section « Resources » listant les références classiques liées au sujet (documentation, articles, tutoriels, etc.), ainsi que la description de l’utilisation de l’IA — en précisant pour quelles tâches et quelles parties du projet.

➠ Des sections supplémentaires peuvent être requises selon le projet (par exemple des exemples d’utilisation, une liste de fonctionnalités, des choix techniques, etc.).

Toutes les additions requises seront explicitement listées ci-dessous.

• Une description détaillée de vos choix d’algorithme et de la stratégie d’implémentation doit également être incluse.
• Une documentation des fonctionnalités de représentation visuelle et de la façon dont elles améliorent l’expérience utilisateur.
• Un exemple d’entrée et de sortie attendue démontrant la fonctionnalité du programme.

Votre README doit être rédigé en anglais.

9

## Chapitre IX
### Partie bonus

Cette partie bonus ne sera revue que si toutes les exigences obligatoires sont remplies.

Voici des fonctionnalités que vous pouvez implémenter pour améliorer votre projet :

• Performance exceptionnelle :
  ◦ vous répondez « parfaitement » aux cibles de performance de référence pour toutes les cartes fournies ;
  ◦ « parfaitement » signifie que vous atteignez ou dépassez le nombre de tours cible.
• Carte challenger :
  ◦ la carte The Impossible Dream est résolue et bat le record de référence de 45 tours.

10

## Chapitre X
### Soumission et évaluation par les pairs

Soumettez votre devoir dans votre dépôt Git comme d’habitude. Seul le travail présent dans votre dépôt sera évalué pendant l’évaluation par les pairs. N’hésitez pas à vérifier les noms de vos fichiers pour vous assurer qu’ils sont corrects.

Placez tous vos fichiers à la racine de votre dépôt.

Un programme de simulation entièrement fonctionnel écrit en Python, comprenant :

• un parseur pour le format de fichier d’entrée ;
• un moteur de simulation respectant les règles de mouvement et les règles de zone ;
• un algorithme de recherche de chemin (ou plusieurs) capable de minimiser le nombre total de tours ;
• un système de représentation visuelle (couleurs terminal et/ou interface graphique) ;
• une sortie terminale ou un journal respectant le format spécifié.

Notez que l’on peut vous demander d’expliquer votre code ou même d’écrire du code. Assurez-vous d’être prêt à cela.

Les cartes d’évaluation peuvent être différentes de celles fournies dans le sujet.

Pendant l’évaluation, une légère modification du projet peut parfois être demandée. Cela peut concerner un changement mineur de comportement, quelques lignes de code à écrire ou réécrire, ou une fonctionnalité facile à ajouter.

Même si cette étape ne s’applique pas à chaque projet, vous devez être prêt si elle est mentionnée dans les consignes d’évaluation.

Cette étape sert à vérifier votre compréhension réelle d’une partie précise du projet.

La modification peut être réalisée dans n’importe quel environnement de développement de votre choix (par exemple votre configuration habituelle), et elle doit être réalisable en quelques minutes — sauf si un délai précis est défini dans le cadre de l’évaluation.

Vous pouvez par exemple être demandé de faire une petite mise à jour d’une fonction ou d’un script, de modifier un affichage, ou d’ajuster une structure de données pour stocker de nouvelles informations, etc.

Les détails (portée, cible, etc.) seront précisés dans les consignes d’évaluation et peuvent varier d’une évaluation à l’autre pour un même projet.

23
