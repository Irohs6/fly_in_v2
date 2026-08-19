import math


class ValidationError(Exception):
    """Erreur de validation de la carte."""
    pass


class MapValidator:
    """Valide la configuration issue du parser selon les règles Fly-in."""

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
    VALID_HUB_KEYS = {"zone_type", "color", "capacity"}
    VALID_CONN_KEYS = {"capacity"}

    def __init__(
        self,
        nb_drones,
        start_hub,
        end_hub,
        hubs,
        connections,
        zone_entries,
        connection_entries,
    ):
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections
        self.zone_entries = zone_entries
        self.connection_entries = connection_entries

    def validate(self) -> None:
        """Valide toutes les sections du fichier."""
        self._validate_nb_drones()
        self._validate_zones()
        self._validate_connections()
        self._check_unique_zone_names()
        self._check_connection_endpoints()
        self._check_duplicate_connections()

    def _validate_nb_drones(self) -> None:
        if not isinstance(self.nb_drones, int):
            raise ValidationError(
                "Ligne 1: définition nb_drones manquante."
            )
        if self.nb_drones <= 0:
            raise ValidationError(
                "Ligne 1: le nombre de drones doit être positif."
            )

    def _validate_zones(self) -> None:
        """Valide les hubs et leurs métadonnées."""
        for hub, line in self.zone_entries:

            # Vérification du type de zone
            zone_type = hub.get("zone_type", "normal")
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ValidationError(
                    f"Ligne {line}: zone invalide '{zone_type}' "
                    f"pour le hub {hub['name']!r}"
                )

            # Vérification des clés inconnues
            extra_keys = {
                key
                for key in hub.keys()
                if key not in {
                    "name",
                    "x",
                    "y",
                    "zone_type",
                    "color",
                    "capacity",
                }
            }
            for key in extra_keys:
                raise ValidationError(
                    f"Ligne {line}: clé de métadonnée inconnue '{key}' "
                    f"pour le hub {hub['name']!r}"
                )

            # Vérification de la capacité
            capacity = hub["capacity"]
            is_terminal_hub = hub is self.start_hub or hub is self.end_hub

            if is_terminal_hub and capacity == math.inf:
                continue

            if not isinstance(capacity, int) or capacity < 1:
                raise ValidationError(
                    f"Ligne {line}: capacité invalide "
                    f"pour le hub {hub['name']!r}"
                )

    def _validate_connections(self) -> None:
        for connection, line in self.connection_entries:

            # Vérification des clés inconnues
            extra_keys = {
                key
                for key in connection.keys()
                if key not in {
                    "source",
                    "target",
                    "capacity",
                }
            }
            for key in extra_keys:
                raise ValidationError(
                    f"Ligne {line}: clé de métadonnée inconnue '{key}' "
                    "pour la connexion "
                    f"{connection['source']!r}-{connection['target']!r}"
                )

            # Vérification de la capacité
            cap = connection["capacity"]
            if not isinstance(cap, int) or cap <= 0:
                raise ValidationError(
                    f"Ligne {line}: capacité de lien invalide "
                    "pour la connexion "
                    f"{connection['source']!r}-{connection['target']!r}"
                )

    def _check_unique_zone_names(self) -> None:
        names: dict[str, int] = {}
        for hub, line in self.zone_entries:
            name = hub["name"]
            if name in names:
                first_line = names[name]
                raise ValidationError(
                    f"Ligne {line}: nom de hub dupliqué: {name!r} "
                    f"(déjà défini ligne {first_line})"
                )
            names[name] = line

    def _check_connection_endpoints(self) -> None:
        known_names = {self.start_hub["name"], self.end_hub["name"]}
        known_names.update(hub["name"] for hub in self.hubs)

        for connection, line in self.connection_entries:
            if connection["source"] not in known_names:
                raise ValidationError(
                    f"Ligne {line}: connexion vers hub inconnu: "
                    f"{connection['source']!r}"
                )
            if connection["target"] not in known_names:
                raise ValidationError(
                    f"Ligne {line}: connexion vers hub inconnu: "
                    f"{connection['target']!r}"
                )

    def _check_duplicate_connections(self) -> None:
        checked_conn: dict[tuple[str, str], int] = {}
        for connection, line in self.connection_entries:
            pair = tuple(sorted([connection["source"], connection["target"]]))
            if pair in checked_conn:
                first_line = checked_conn[pair]
                raise ValidationError(
                    f"Ligne {line}: "
                    f"Connexion dupliquée entre {pair[0]} et {pair[1]} "
                    f"(déjà définie ligne {first_line})"
                )
            checked_conn[pair] = line
