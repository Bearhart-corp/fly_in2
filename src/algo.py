from collections import defaultdict
import heapq
import itertools
from .enumeration import ZoneType
from src.domain_class import Zone, Drone
from .graph import Graph
from typing import DefaultDict, List, Tuple


class Algo2:

    def __init__(self, graph: Graph, start: Zone, end: Zone) -> None:
        self.graph = graph
        self.start = start
        self.end = end
        self._id_ = itertools.count()

    def algo(self, graph: Graph) -> None:
        # (zone_name, turn) -> nb drones
        zone_usage: DefaultDict = defaultdict(int)
        # ((src, dst), turn) -> nb drones
        edge_usage: DefaultDict = defaultdict(int)
        for drone in graph.drones:
            path = self.find_path(graph, zone_usage, edge_usage)
            self.apply_path(drone, path)
            self.update_usage(path, zone_usage, edge_usage)

    def find_path(
        self,
        graph: Graph,
        zone_cap: DefaultDict,
        edge_cap: DefaultDict
    ) -> List[Tuple[Zone, Zone]]:
        # STATE = (zone, turn)
        start_state = (self.start, 0)
        # heap:
        # (distance, unique_id, state)
        pq: List = []
        heapq.heappush(
            pq,
            (0, next(self._id_), start_state)
        )
        # coût minimal pour atteindre un état
        cost: DefaultDict = defaultdict(lambda: float("inf"))
        cost[start_state] = 0
        parent: dict = {}
        while pq:
            cur_dist, _, cur_state = heapq.heappop(pq)
            cur_zone, cur_turn = cur_state
            if cur_zone == self.end:
                return self.reconstruct(parent, cur_state)
            neighbors = graph.get_neighbors(cur_zone.name)
            for con in neighbors:
                nxt = con.dest
                if nxt.metadata.zone_type == "blocked":
                    continue
                move_cost = ZoneType.zone.get(
                    nxt.metadata.zone_type
                )
                nxt_turn = cur_turn + move_cost
                nxt_state = (nxt, nxt_turn)
                if (
                    zone_cap[(nxt.name, nxt_turn)]
                    >= nxt.metadata.max_drones
                ):
                    continue
                if (
                    edge_cap[((
                        con.src.name,
                        con.dest.name),
                        nxt_turn)] >= con.metadata.max_link_capacity
                ):
                    continue
                new_cost = cur_dist + move_cost
                if new_cost < cost[nxt_state]:
                    cost[nxt_state] = new_cost
                    parent[nxt_state] = cur_state
                    heapq.heappush(
                        pq,
                        (
                            new_cost,
                            next(self._id_),
                            nxt_state
                        )
                    )
            wait_turn = cur_turn + 1
            wait_state = (cur_zone, wait_turn)
            if (
                zone_cap[(cur_zone.name, wait_turn)]
                < cur_zone.metadata.max_drones
            ):
                wait_cost = cur_dist + 1
                if wait_cost < cost[wait_state]:
                    cost[wait_state] = wait_cost
                    parent[wait_state] = cur_state
                    heapq.heappush(
                        pq,
                        (
                            wait_cost,
                            next(self._id_),
                            wait_state
                        )
                    )
        raise Exception("No path found")

    def reconstruct(
        self,
        parent: dict[tuple[Zone, int], tuple[Zone, int]],
        end_state: tuple[Zone, int]
    ) -> List[Tuple[Zone, Zone]]:
        path: list = []
        cur_state = end_state
        while cur_state in parent:
            prev_state = parent[cur_state]
            path.append((prev_state[0], cur_state[0]))
            cur_state = prev_state
        path.reverse()
        return path

    def apply_path(
        self,
        drone: Drone,
        path: List[Tuple[Zone, Zone]]
    ) -> None:
        if not path:
            return
        drone.moves.append((path[0][0].x, path[0][0].y))
        for _, dest in path:
            drone.moves.append((dest.x, dest.y))

    def update_usage(
        self,
        path: List[Tuple],
        zone_cap: DefaultDict,
        edge_cap: DefaultDict
    ) -> None:
        if not path:
            return
        zone_cap[(path[0][0].name, 0)] += 1
        turn = 1
        for src, dest in path:
            move_cost = ZoneType.zone[dest.metadata.zone_type]
            turn += move_cost - 1
            zone_cap[(dest.name, turn)] += 1
            edge_cap[
                (
                    (src.name, dest.name),
                    turn
                )
            ] += 1
            turn += 1
