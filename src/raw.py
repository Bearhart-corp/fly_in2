from typing import Optional


class RawHub:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        metadata: Optional[dict[str, str]],
        kind: str  # "start_hub", "end_hub", "hub"
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.metadata = metadata
        self.kind = kind


class RawConnection:
    def __init__(
        self,
        a: str,
        b: str,
        metadata: Optional[dict[str, str]]
    ) -> None:
        self.a = a
        self.b = b
        self.metadata = metadata


class RawMap:
    def __init__(
        self,
        nb_drones: int,
        hubs: list[RawHub],
        connections: list[RawConnection]
    ) -> None:
        self.nb_drones = nb_drones
        self.hubs = hubs
        self.connections = connections
