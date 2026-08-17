# Robustesse appliquée : étape 1, 2 et 3

## Objectif

Renforcer le moteur de simulation pour qu’il reste stable sur les cartes plus complexes, en particulier lorsque plusieurs drones se bloquent dans des boucles, saturent des zones ou réutilisent des chemins déjà congestionnés.

## Étape 1 — Prévention des deadlocks sur chemins cycliques

### Ce qui a été ajouté

Dans [src/model/simulation.py](../src/model/simulation.py), j’ai ajouté :

- un instantané de l’état de la simulation via `_progress_snapshot()`,
- une détection des blocs répétés via `_should_reroute_stalled()`,
- une liste de snapshots récents (`_stall_history`) pour repérer les répétitions de blocage,
- un reroutage renforcé avec `force=True` dès qu’un même schéma de blocage revient.

### Pourquoi c’était utile

La simulation détectait un blocage final après un nombre de tours fixe, mais elle ne distinguait pas vraiment entre :

- un vrai deadlock structurel,
- un simple blocage temporaire,
- un cycle de rééchec qui se reproduit exactement.

Le correctif permet d’éviter d’attendre trop longtemps avant de replanifier les drones en difficulté.

## Étape 2 — Gestion plus stricte des capacités de zone

### Ce qui a été ajouté

Dans [src/model/simulation.py](../src/model/simulation.py), j’ai introduit une garde explicite `_can_move_to()` :

- la connexion doit avoir de la place,
- la zone cible doit avoir de la place,
- aucun mouvement ne part sans validation préalable.

### Bénéfice

Les drones ne peuvent plus tenter un déplacement qui violates immédiatement les contraintes de capacité. Cela évite les cas où plusieurs drones se “décident” d’un mouvement impossible, puis restent bloqués dans un état incohérent.

## Étape 3 — Reroutage amélioré pour plusieurs drones bloqués

### Ce qui a été ajouté

Dans [src/model/simulation.py](../src/model/simulation.py), la méthode `_reroute_stalled_drones()` a été renforcée :

- elle peut forcer un reroutage (`force=True`),
- elle bloque explicitement les zones saturées et les zones déjà pleines,
- elle replanifie les drones “en attente” avec un chemin alternatif,
- elle évite qu’un simple drone bloqué reste figé pendant des tours entiers sans tentative de réparation.

### Pourquoi c’est important

Sur des cartes complexes, un seul drone bloqué peut contaminer le reste de la flotte. Le reroutage forcé permet de rééquilibrer rapidement les chemins et évite d’enchaîner les faux deadlocks.

## Modifications complémentaires déjà nécessaires

Avant cette robustesse, plusieurs problèmes de structure avaient déjà été corrigés :

- création des objets `Connection` dans [src/controller/controller.py](../src/controller/controller.py),
- cohérence du statut de transit dans [src/model/drone.py](../src/model/drone.py),
- libération correcte des réservations dans [src/model/simulation.py](../src/model/simulation.py),
- compatibilité de l’API de connexion dans [src/model/connection.py](../src/model/connection.py),
- alias `zones` dans [src/model/graph.py](../src/model/graph.py) pour la vue.

## Validation

Commande exécutée :

```bash
cd /home/gacattan/Desktop/fly_in_v2 && PYTHONPATH=. pytest -q tests/test_robustness.py
```

Résultat obtenu :

- `2 passed in 0.02s`

Commande de validation réelle sur le cas de référence :

```bash
cd /home/gacattan/Desktop/fly_in_v2 && PYTHONPATH=. python - <<'PY'
from src.controller.controller import Controller

controller = Controller('assets/maps/easy/01_linear_path.txt')
print('turns:', controller.simulation.turn)
print('final statuses:', {d.drone_id: d.status for d in controller.simulation.drones})
print('replay frames:', len(controller.simulation.replay_frames))
PY
```

Résultat obtenu :

- `turns: 9`
- `final statuses: {'D1': 'finished', 'D2': 'finished'}`

La simulation reste compatible avec le cas de base tout en ajoutant la robustesse nécessaire sur les cartes plus complexes.
