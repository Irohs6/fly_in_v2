# Diagnostic du deadlock de la simulation Fly-in

## Observation

La commande suivante reproduit le problème dans le projet :

```bash
make run MAP=assets/maps/easy/01_linear_path.txt
```

Le programme échoue ensuite avec une erreur de type `GraphError: Deadlock: no progress after 9 stalled turns.` ou, selon la version du code exécutée, avec une erreur de type `TypeError` sur `moving_connection[1]`.

## Cause racine

Le cœur du problème se trouve dans la logique de simulation dans [src/model/simulation.py](../src/model/simulation.py#L140-L188).

Les éléments importants sont :

1. La simulation détermine si un tour a fait des progrès avec cette logique :
   - si aucun drone n’a bougé,
   - et aucun drone n’est en transit,
   - alors elle considère que la simulation est en panne.
2. Quand ce cas se reproduit suffisamment de fois, elle lève une erreur de deadlock :
   - `max_stall = len(self.drones) * len(self.graph.hubs) + 1`
   - puis `if stalled_turns >= max_stall: raise GraphError(...)`
3. La raison de cette stagnation est que l’état interne des drones est incohérent ou incomplet :
   - dans [src/model/drone.py](../src/model/drone.py#L5-L29), `moving_connection` est parfois `None`,
   - mais le code de simulation le traite ensuite comme un tuple indexable (`drone.moving_connection[1]`).

Cela crée un état où la simulation ne sait plus distinguer clairement :

- drone immobile,
- drone en transit,
- drone en attente,
- drone qui a fini.

Au lieu d’avancer de façon fiable, elle passe par des tours où aucune action réelle n’est possible, puis déclenche le deadlock détecté.

## Pourquoi cela arrive sans avoir modifié le code

Le bug n’est pas lié à une carte magique ou à une “mauvaise configuration utilisateur”.

Il vient directement de l’implémentation actuelle :

- [src/model/simulation.py](../src/model/simulation.py#L80-L118) manipule le chemin, les connexions et les états des drones,
- [src/model/drone.py](../src/model/drone.py#L5-L29) garde des informations de transit dans `moving_connection`,
- [src/model/hub.py](../src/model/hub.py#L12-L40) et [src/model/connection.py](../src/model/connection.py#L5-L41) imposent des contraintes de capacité et de coût,
- la détection de deadlock est seulement le symptôme final : elle signale qu’aucun progress n’a été observé pendant plusieurs tours.

Autrement dit, le programme est déjà dans un état bloqué avant l’exception : le deadlock est simplement la dernière étape visible.

## Conclusion

Le problème n’est pas “le code est bien, mais la carte est impossible”.

Le problème est structurel : la simulation ne gère pas correctement les états de transit et de blocage, ce qui conduit à un état de stagnation détecté comme deadlock. Le signal `Deadlock: no progress after 9 stalled turns.` est donc la conséquence d’un état interne incohérent, pas la cause première.

## Fichiers clés à relire

- [src/model/simulation.py](../src/model/simulation.py)
- [src/model/drone.py](../src/model/drone.py)
- [src/model/hub.py](../src/model/hub.py)
- [src/model/connection.py](../src/model/connection.py)
- [assets/maps/easy/01_linear_path.txt](../assets/maps/easy/01_linear_path.txt)
