from typing import Tuple, List, Optional


class ZoneMetadata:
    def __init__(
        self,
        zone_type: str = "normal",
        max_drones: int = 1,
        color: Tuple[int, int, int] | None = (0, 0, 0)
    ) -> None:
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color


class ConnectionMetadata:
    def __init__(
        self,
        max_link_capacity: int = 1
    ) -> None:
        self.max_link_capacity = max_link_capacity


class Zone:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        metadata: ZoneMetadata | None,
        is_start: bool = False,
        is_end: bool = False
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        if not metadata:
            self.metadata = ZoneMetadata()
        else:
            self.metadata = metadata
        self.is_start = is_start
        self.is_end = is_end
        self.drones: List[Tuple[Drone, int]] = []


class Drone:
    def __init__(self, id: int) -> None:
        self.id = id
        self.moves: List[Tuple[int, int]] = []
        self.logs = []


class Connection:
    def __init__(
        self,
        src: Zone,  # nom zone
        dest: Zone,
        metadata: ConnectionMetadata
    ) -> None:
        self.src = src
        self.dest = dest
        if metadata:
           self.metadata = metadata
        else:
            self.metadata = ConnectionMetadata()
