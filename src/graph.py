from .raw import RawHub, RawConnection, RawMap
from .domain_class import Connection, Zone, ZoneMetadata, \
    ConnectionMetadata, Drone
from .enumeration import ZoneType, Color
from typing import List


class Graph:
    def __init__(self, nb_drones: int) -> None:
        self.nb_drones: int = nb_drones
        self.zones: dict[str, Zone] = {}
        self.neighbors: dict[str, list[Connection]] = {}
        self.drones: List[Drone] = [Drone(i) for i in range(self.nb_drones)]

    def add_zone(self, zone: Zone) -> None:
        if zone:
            self.zones[zone.name] = zone
            self.neighbors[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        src, dst = connection.src.name, connection.dest.name
        if src not in self.neighbors:
            self.neighbors[src] = []
        if dst not in self.neighbors:
            self.neighbors[dst] = []
        reverse = Connection(
            src=connection.dest,
            dest=connection.src,
            metadata=connection.metadata
        )
        self.neighbors[src].append(connection)
        self.neighbors[dst].append(reverse)

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        return self.neighbors.get(zone_name, [])

    def get_zone_obj(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)


class GraphBuilder:
    def __init__(self, nb_drones: int) -> None:
        self.graph = Graph(nb_drones)
        self.connec_seen: set[str] = set()

    def build(self, raw: RawMap) -> tuple[Graph, str, str]:
        """
        return:
        - graph
        - start_zone_name
        - end_zone_name
        """
        if raw.nb_drones < 1:
            raise BuildError(
                f"nb_drones = {raw.nb_drones} ,"
                "numbers of drones has to be positive"
            )
        for hub in raw.hubs:
            self.graph.add_zone(self._build_zone(hub, raw.nb_drones))
        st, end = self._validate_unique_start_end(raw.hubs)
        for connection in raw.connections:
            self.graph.add_connection(self._build_connection(connection))
        return (self.graph, st, end)

    def _build_zone(self, raw: RawHub, nb_drones: int) -> Zone:
        if raw.name in self.graph.zones:
            raise BuildError(
                f"{raw.kind} is duplicated"
            )
        return Zone(
            name=raw.name,
            x=raw.x,
            y=raw.y,
            metadata=self._build_zone_metadata(
                raw.metadata, raw.kind, nb_drones),
            is_start=(True if raw.kind == "start_hub" else False),
            is_end=(True if raw.kind == "end_hub" else False)
        )

    def _build_zone_metadata(
            self, raw_meta: dict[str, str] | None,
            kind: str, nb_drones: int) -> ZoneMetadata:
        zone_type = "normal"
        color = (0, 0, 0)
        max_drones = 1
        if not raw_meta:
            return ZoneMetadata()
        for k, v in raw_meta.items():
            if k == "max_drones":
                try:
                    max_drones = int(v)
                    if max_drones < 1:
                        raise BuildError("max_drones has to be positive")
                except BuildError as e:
                    raise BuildError(e)
            elif k == "zone":
                if not ZoneType.zone.get(v):
                    raise BuildError(
                        f"{v} doesn't exist in Zone types")
                else:
                    zone_type = v
            elif k == "color":
                try:
                    color = Color.get(v)
                except KeyError:
                    raise BuildError(
                        f"{v} doesn't exist in Color")
            else:
                raise BuildError(f"wrong metadata entry {raw_meta}")
            if kind == "start_hub" or kind == "end_hub":
                max_drones = nb_drones
        return ZoneMetadata(
            zone_type=zone_type, max_drones=max_drones, color=color)

    def _validate_unique_start_end(self,
                                   hubs: list[RawHub]) -> tuple[str, str]:
        flag_s = [h.name for h in hubs if h.kind == "start_hub"]
        flag_end = [h.name for h in hubs if h.kind == "end_hub"]
        if len(flag_s) != 1 or len(flag_end) != 1:
            raise BuildError(
                "duplicate content of start_hub or end_hub"
            )
        return (flag_s[0], flag_end[0])

    def _build_connection(self, raw: RawConnection) -> Connection:
        if not self.graph.zones.get(raw.a) \
                or not self.graph.zones.get(raw.b):
            raise BuildError(
                f"connections: {raw.a} or {raw.b} doesn't exist"
            )
        double = str(sorted((raw.a, raw.b)))
        if double in self.connec_seen:
            raise BuildError(
                f"connection {raw.a}-{raw.b} already exist"
            )
        self.connec_seen.add(double)
        return Connection(
            src=self.graph.zones[raw.a],
            dest=self.graph.zones[raw.b],
            metadata=self._build_connection_metadata(raw.metadata)
        )

    def _build_connection_metadata(self,
                                   raw_meta: dict[str, str] | None
                                   ) -> ConnectionMetadata:
        if not raw_meta:
            return ConnectionMetadata()
        if len(raw_meta) != 1:
            raise BuildError(f"invalid connection metadata: {raw_meta}")
        else:
            k, v = next(iter(raw_meta.items()))
            if k != "max_link_capacity":
                raise BuildError(f"bad formating of {k}")
            try:
                integer = int(v)
            except ValueError as e:
                raise BuildError(f"{e} for the key {k}")
            if integer < 1:
                raise BuildError(f"{v} is not positive or is equal to 0")
        return ConnectionMetadata(
            max_link_capacity=integer
        )

    def _validate_connections(self, graph: Graph) -> None:
        ...


class BuildError(Exception):
    ...
