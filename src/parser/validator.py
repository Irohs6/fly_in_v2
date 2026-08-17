import math


class ValidationError(Exception):
    """Erreur de validation de la carte."""
    pass


class MapValidator:
    """Valide la configuration issue du parser selon les règles Fly-in."""

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
    VALID_HUB_KEYS = {"zone_type", "color", "capacity"}
    VALID_CONN_KEYS = {"capacity"}

    def __init__(self, nb_drones, start_hub, end_hub, hubs, connections):
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections

    def validate(self):
        """Valide toutes les sections du fichier."""
        self._validate_nb_drones()
        self._validate_zones()
        self._validate_connections()
        self._check_unique_zone_names()
        self._check_connection_endpoints()
        self._check_duplicate_connections()

    def _validate_nb_drones(self):
        if not isinstance(self.nb_drones, int):
            raise ValidationError("Définition nb_drones manquante.")
        if self.nb_drones <= 0:
            raise ValidationError("Le nombre de drones doit être positif.")

    def _validate_zones(self):
        """Valide les hubs et leurs métadonnées."""
        for hub in self.hubs + [self.start_hub, self.end_hub]:

            # Vérification du type de zone
            zone_type = hub.get("zone_type", "normal")
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ValidationError(
                    f"Zone invalide '{zone_type}' à la ligne {hub['line']}"
                )

            # Vérification des clés inconnues
            extra_keys = {
                key
                for key in hub.keys()
                if key not in {
                    "name",
                    "x",
                    "y",
                    "line",
                    "zone_type",
                    "color",
                    "capacity",
                }
            }
            for key in extra_keys:
                raise ValidationError(
                    f"Clé de métadonnée inconnue '{key}' à la ligne "
                    f"{hub['line']}"
                )

            # Vérification de la capacité
            capacity = hub["capacity"]
            is_terminal_hub = hub is self.start_hub or hub is self.end_hub

            if is_terminal_hub and capacity == math.inf:
                continue

            if not isinstance(capacity, int) or capacity < 1:
                raise ValidationError(
                    f"Capacité invalide à la ligne {hub['line']}"
                )

    def _validate_connections(self):
        for connection in self.connections:

            # Vérification des clés inconnues
            extra_keys = {
                key
                for key in connection.keys()
                if key not in {
                    "source",
                    "target",
                    "line",
                    "capacity",
                }
            }
            for key in extra_keys:
                raise ValidationError(
                    f"Clé de métadonnée inconnue '{key}' "
                    f"à la ligne {connection['line']}"
                )

            # Vérification de la capacité
            cap = connection["capacity"]
            if not isinstance(cap, int) or cap <= 0:
                raise ValidationError(
                    f"Capacité de lien invalide à la ligne "
                    f"{connection['line']}"
                )

    def _check_unique_zone_names(self):
        names = set()
        for hub in [self.start_hub, *self.hubs, self.end_hub]:
            name = hub["name"]
            if name in names:
                raise ValidationError(f"Nom de hub dupliqué: {name!r}")
            names.add(name)

    def _check_connection_endpoints(self):
        known_names = {self.start_hub["name"], self.end_hub["name"]}
        known_names.update(hub["name"] for hub in self.hubs)

        for connection in self.connections:
            if connection["source"] not in known_names:
                raise ValidationError(
                    f"Connexion vers hub inconnu: {connection['source']!r} "
                    f"(ligne {connection['line']})"
                )
            if connection["target"] not in known_names:
                raise ValidationError(
                    f"Connexion vers hub inconnu: {connection['target']!r} "
                    f"(ligne {connection['line']})"
                )

    def _check_duplicate_connections(self):
        checked_conn = set()
        for connection in self.connections:
            pair = tuple(sorted([connection["source"], connection["target"]]))
            if pair in checked_conn:
                raise ValidationError(
                    f"Connexion dupliquée entre {pair[0]} et {pair[1]} "
                    f"(ligne {connection['line']})"
                )
            checked_conn.add(pair)
