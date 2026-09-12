from .hub import Hub
from .errors import ConnectionError


class Connection:
    """Connexion bidirectionnelle avec capacité et occupation courante."""
    def __init__(self, source: Hub, target: Hub, capacity: int | float):
        """Relie source et target avec la capacité donnée et une occupation
        nulle.
        """
        self.source = source
        self.target = target
        self.capacity = capacity
        self.nb_drones = 0

    def add_nb_drone(self) -> None:
        """Ajoute toujours 1 drone, jamais plus."""
        if self.nb_drones + 1 > self.capacity:
            raise ConnectionError(
                "Cannot add more drones than the maximum allowed"
            )
        self.nb_drones += 1

    def is_available(self) -> bool:
        """Indique si la connexion peut accueillir un drone supplémentaire."""
        return self.nb_drones < self.capacity

    def get_extremities(self, hub: Hub) -> Hub:
        """Retourne l’autre extrémité de la connexion.

        Lève ConnectionError si hub ne fait pas partie de la connexion.
        """
        if self.source is hub:
            return self.target

        if self.target is hub:
            return self.source

        raise ConnectionError(
            f"Hub {hub.name} is not connected by this connection."
        )

    def __repr__(self) -> str:
        """Retourne une représentation détaillée de la connexion pour le
        débogage.
        """
        return (
            f"Connection(source={self.source.name}, target={self.target.name},"
            f" capacity={self.capacity}, nb_drones={self.nb_drones})"
        )
