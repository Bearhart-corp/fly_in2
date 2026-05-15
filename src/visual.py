from math import ceil
import pygame
from pygame.font import Font
from .asset import screen_size
from typing import Tuple, List
from .graph import Graph
from .domain_class import Zone
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_r
)


class Vector():
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, other: float) -> "Vector":
        return Vector(self.x * other, self.y * other)

    def to_tuple(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))


class CoordinateMapper:
    def __init__(self, zones: dict[str, Zone]) -> None:
        xs = [z.x for z in zones.values()]
        ys = [z.y for z in zones.values()]
        self.min_xy = (min(xs), min(ys))
        self.max_xy = (max(xs), max(ys))

    def to_screen(self, x: int, y: int) -> Tuple[int, int]:
        return (
            x - self.min_xy[0],
            y - self.min_xy[1]
        )

    def range_coor(self, y: bool) -> int:
        return len([i for i in range(self.min_xy[y], self.max_xy[y])]) + 1


class HubSize:
    range_y: int
    range_x: int
    pad: int
    full_size: int
    size: int

    @classmethod
    def init(cls,
             w: int,
             h: int,
             mapper: CoordinateMapper) -> None:

        cls.range_y = mapper.range_coor(y=True)
        cls.range_x = mapper.range_coor(y=False)

        size = cls.hub_size(w, h, cls.range_x, cls.range_y)

        cls.pad = size // 2
        cls.full_size = size
        cls.size = size - cls.pad
        cls.bloc = cls.range_y * cls.full_size
        cls.center = (h - cls.bloc) >> 1

    @classmethod
    def hub_size(cls, w: int, h: int, x: int, y: int) -> int:
        return max(100, min(w // x, h // y))


class Visual:
    @staticmethod
    def launch_visualization(graph: Graph) -> None:
        pygame.init()
        w, h = screen_size.screen_size()
        mapper = CoordinateMapper(graph.zones)
        HubSize.init(w, h, mapper)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, HubSize.size // 5)
        screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        pygame.display.set_caption("Fly In 🐝")
        tile = pygame.image.load("bg/dalle.png")
        img_w, img_h = tile.get_size()
        ratio_w = max(1, ceil(w / img_w))
        ratio_h = max(1, ceil(h / img_h))
        static_surf = pygame.Surface((w, h))
        for i in range(ratio_h):
                for j in range(ratio_w):
                    static_surf.blit(tile, (j * img_w, i * img_h))
        img = pygame.image.load("drones_img/drones.png")
        img = pygame.transform.smoothscale(img,
                                           (HubSize.size, HubSize.size))
        b_img = pygame.image.load("hubs_img/hub.png").convert_alpha()
        b_img = pygame.transform.smoothscale(b_img,
                                             (HubSize.size, HubSize.size))
        turn = 0
        max_len = max(len(drone.moves) for drone in graph.drones)
        t = 0.0
        speed = 1000.0  # 1sec
        arg = Visual._update_lines(graph, mapper, HubSize.bloc)
        all_pos = []
        for z in graph.zones.values():
            x, y = mapper.to_screen(z.x, z.y)
            all_pos.append(Visual.grid2screen(x, y, HubSize.center, 0))
        running = True
        while running:
            dt = clock.tick(60) / speed
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_r:
                        turn = 0
                    if event.key == pygame.K_UP:
                        speed *= 0.8
                    if event.key == pygame.K_DOWN:
                        speed *= 1.2
                elif event.type == QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    w, h = pygame.display.get_surface().get_size()
                    w, h = event.w, event.h
                    ratio_w = max(1, ceil(w / img_w))
                    ratio_h = max(1, ceil(h / img_h))
                    for i in range(ratio_h):
                        for j in range(ratio_w):
                            static_surf.blit(tile, (j * img_w, i * img_h))
                    HubSize.init(w, h, mapper)
                    font = pygame.font.Font(None, HubSize.size // 5)
                    img = pygame.image.load("drones_img/drones.png")
                    img = pygame.transform.smoothscale(img,
                                                    (HubSize.size, HubSize.size))
                    b_img = pygame.image.load("hubs_img/hub.png").convert_alpha()
                    b_img = pygame.transform.smoothscale(b_img,
                                                        (HubSize.size, HubSize.size))
                    arg = Visual._update_lines(graph, mapper, HubSize.center)
                    all_pos = []
                    for z in graph.zones.values():
                        x, y = mapper.to_screen(z.x, z.y)
                        all_pos.append(Visual.grid2screen(x, y, HubSize.center, 0))
            t += dt
            if t >= 1:
                t = 0
                turn += 1
            turn = min(turn, max_len - 1)
            Visual._draw_lines(static_surf, arg)
            Visual._draw_hubs(graph.zones, static_surf, font, b_img, all_pos)
            screen.blit(static_surf, (0, 0))
            Visual._create_drones(
                graph, screen, mapper, HubSize.center, img, font, turn, t)
            pygame.display.flip()
        pygame.quit()

    @staticmethod
    def _create_drones(graph: Graph,
                       screen: pygame.Surface,
                       mapper: CoordinateMapper,
                       center: int,
                       img: pygame.Surface,
                       font: Font,
                       turn: int,
                       t: float) -> None:
        for drone in graph.drones:
            if not drone.moves:
                continue
            i = min(turn, len(drone.moves) - 1)
            j = min(i + 1, len(drone.moves) - 1)
            x, y = drone.moves[i]
            x1, y1 = drone.moves[j]
            x, y = mapper.to_screen(x, y)
            x1, y1 = mapper.to_screen(x1, y1)
            x, y = Visual.grid2screen(x, y, center, 0)
            x1, y1 = Visual.grid2screen(x1, y1, center, 0)
            src = Vector(x, y)
            dst = Vector(x1, y1)
            pos = src + (dst - src) * t
            screen.blit(img, pos.to_tuple())
            text_surface = font.render(str(drone.id), True, (255, 255, 255))
            calcul = pos + Vector(HubSize.size // 2, HubSize.size // 2)
            screen.blit(text_surface, calcul.to_tuple())
            Visual.show_turn(turn, font, screen)

    @staticmethod
    def show_turn(turn: int,
                  font: Font, screen: pygame.Surface) -> None:
        text_surface = font.render(
            "Number of turn: " + str(turn), True, (255, 255, 255))
        screen.blit(text_surface, (100, 100))

    @staticmethod
    def _draw_hubs(
            zones: dict[str, Zone], screen: pygame.Surface,
            font: Font, b_img: pygame.Surface,
            all_pos: List[Tuple[int, int]]) -> None:
        size20 = HubSize.size // 5
        size33 = HubSize.size // 3
        size50 = HubSize.size // 2
        for i, zone in enumerate(zones.values()):
            pos = all_pos[i]
            img = b_img.copy()
            if zone.metadata.color is None:
                continue
            rgba = (*zone.metadata.color, 10)
            filter = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            filter.fill(rgba)
            img.blit(filter, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(img, pos)
            x, y = pos
            text_surface = font.render(zone.name, True, (255, 255, 255))
            screen.blit(text_surface, (x, y - size20))
            text_surface = font.render("MAX_DRONES = " + str(
                zone.metadata.max_drones), True, (255, 255, 255))
            screen.blit(text_surface, (x, y - size33))
            text_surface = font.render(
                zone.metadata.zone_type, True, (255, 255, 255))
            screen.blit(text_surface, (x, y - size50))

    @staticmethod
    def _draw_lines(static_surf: pygame.Surface, args: List[list]) -> None:
        for lst in args:
            xy1, xy2, size = lst
            pygame.draw.line(static_surf, (255, 255, 255), xy1, xy2, size)
    
    def _update_lines(graph: Graph,
                      mapper: CoordinateMapper,
                      size_bloc: int) -> List[List]:
        middle_cell = (HubSize.size // 2)
        size = HubSize.size // 22
        res = []
        for edges in graph.neighbors.values():
            for edge in edges:
                x1, y1 = mapper.to_screen(edge.src.x, edge.src.y)
                x2, y2 = mapper.to_screen(edge.dest.x, edge.dest.y)
                xy1 = Visual.grid2screen(x1, y1, size_bloc, middle_cell)
                xy2 = Visual.grid2screen(x2, y2, size_bloc, middle_cell)
                res.append([xy1, xy2, size])
        return res

    @staticmethod
    def grid2screen(x: int, y: int,
                    center: int, middle_cell: int) -> Tuple[int, int]:
        if center == 0:
            center = HubSize.pad // 2
        step = HubSize.size + HubSize.pad
        base_x = HubSize.pad // 2 + x * step
        base_y = center + y * step
        return ((base_x + middle_cell), base_y + middle_cell)
