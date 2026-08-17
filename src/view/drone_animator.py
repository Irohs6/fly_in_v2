"""
Animation des drones + contrôle de replay (version simplifiée).
"""

import pygame
import math
from enum import Enum
from typing import Dict, List, Tuple, Any
from src.view.sprite.drone_sprite import DroneSprite

# ───────────────────────────────────────────────
# Constantes
# ───────────────────────────────────────────────

DRONE_RADIUS = 8
ANIM_DURATION = 1.0

DRONE_COLORS = {
    "moving": (150, 255, 100),
    "idle": (150, 150, 255),
}


class ReplayState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


# ───────────────────────────────────────────────
# Drone animé (interpolation + dessin)
# ───────────────────────────────────────────────
class DisplayInfoHub:
    def __init__(
        self,
        hub_name: str,
        position: Tuple[float, float],
        hub_color: Tuple[int, int, int],
        count: int,
        capacity: int,
    ):
        self.name = hub_name
        self.position = position
        self.color = hub_color
        self.count = count
        self.capacity = capacity

    def display_hub_info(self, screen, font):
        # Nom du hub au-dessus
        name_label = font.render(self.name, True, (220, 220, 220))
        screen.blit(
            name_label,
            (
                self.position[0] - name_label.get_width() // 2,
                self.position[1] - 52,
            ),
        )
        # Occupation en dessous
        cap_label = font.render(
            f"{self.count}/{self.capacity}",
            True,
            self.color,
        )
        screen.blit(
            cap_label,
            (
                self.position[0] - cap_label.get_width() // 2,
                self.position[1] + 36,
            ),
        )


class DisplayInfoDrone:
    def __init__(
        self,
        drone_id: str,
        position: Tuple[float, float],
        drone_color: Tuple[int, int, int],
    ):
        self.id = drone_id
        self.position = position
        self.color = drone_color

    def display_drone_info(self, screen, font):
        label = font.render(self.id, True, self.color)
        screen.blit(
            label,
            (
                self.position[0] + 12,
                self.position[1] - 8,
            ),
        )


class DisplayInfoConnection:
    def __init__(
        self,
        start_hub: str,
        end_hub: str,
        position: Tuple[float, float],
        connection_color: Tuple[int, int, int],
        drone_ids: List[str],
    ):
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.position = position
        self.color = connection_color
        self.drone_ids = drone_ids

    def display_connection_info(self, screen, font):
        # Nom de la connexion (ex: hub1 → hub2)
        conn_label = font.render(
            f"{self.start_hub} → {self.end_hub}",
            True,
            (160, 200, 255),
        )
        # IDs des drones en transit
        drone_label = font.render(
            ", ".join(self.drone_ids),
            True,
            self.color,
        )
        total_h = conn_label.get_height() + drone_label.get_height() + 2
        max_w = max(conn_label.get_width(), drone_label.get_width())
        bg = pygame.Surface((max_w + 10, total_h + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        bx = self.position[0] - max_w // 2
        by = self.position[1] - total_h // 2
        screen.blit(bg, (bx - 5, by - 3))
        screen.blit(
            conn_label, (bx + (max_w - conn_label.get_width()) // 2, by)
        )
        screen.blit(
            drone_label,
            (
                bx + (max_w - drone_label.get_width()) // 2,
                by + conn_label.get_height() + 2,
            ),
        )


class AnimatedDrone:
    def __init__(
        self,
        drone_id: str,
        hub_positions: Dict[str, Tuple[float, float]],
        start_hub: str,
    ):
        self.id = drone_id
        self.hub_positions = hub_positions
        self.start = start_hub
        self.end = start_hub
        self.pos = hub_positions[start_hub]
        self.t = 0.0
        self.moving = False
        self._sprite: DroneSprite | None = None

    @property
    def status(self) -> str:
        return "moving" if self.moving else "idle"

    def set_destination(self, hub: str):
        if hub != self.end:
            self.start = self.end
            self.end = hub
            self.t = 0.0
            self.moving = True

    def update(self, dt: float):
        if not self.moving:
            return

        self.t = min(1.0, self.t + dt / ANIM_DURATION)
        sx, sy = self.hub_positions[self.start]
        ex, ey = self.hub_positions[self.end]

        self.pos = (sx + (ex - sx) * self.t, sy + (ey - sy) * self.t)

        if self.t >= 1.0:
            self.moving = False
            self.pos = self.hub_positions[self.end]

    def draw(self, surf, camera, sw, sh, zoom, font=None):
        x, y = camera.world_to_screen(self.pos[0], self.pos[1], sw, sh)
        if self._sprite is None:
            self._sprite = DroneSprite(self)
        self._sprite.draw(surf, (int(x), int(y)))
        if font is not None:
            color = DRONE_COLORS["moving" if self.moving else "idle"]
            DisplayInfoDrone(
                self.id, (int(x), int(y)), color
            ).display_drone_info(surf, font)


# ───────────────────────────────────────────────
# Contrôleur de replay (play/pause/next/prev)
# ───────────────────────────────────────────────


class ReplayController:
    def __init__(self, total_turns: int, speed: float):
        self.state = ReplayState.STOPPED
        self.turn = 0
        self.total = max(1, total_turns)
        self.speed = speed
        self.timer = 0.0

    def handle_event(self, event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_SPACE:
            self.state = (
                ReplayState.PAUSED
                if self.state == ReplayState.PLAYING
                else ReplayState.PLAYING
            )
            self.timer = 0.0
            return True

        if event.key == pygame.K_RIGHT:
            self.turn = min(self.turn + 1, self.total - 1)
            self.state = ReplayState.PAUSED
            return True

        if event.key == pygame.K_LEFT:
            self.turn = max(self.turn - 1, 0)
            self.state = ReplayState.PAUSED
            return True

        if event.key == pygame.K_r:
            self.turn = 0
            self.state = ReplayState.PLAYING
            self.timer = 0.0
            return True

        return False

    def update(self, dt: float) -> None:
        if self.state != ReplayState.PLAYING:
            self.timer = 0.0
            return

        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0.0
            self.turn = (self.turn + 1) % self.total


# ───────────────────────────────────────────────
# Couche d’animation (mise à jour + dessin)
# ───────────────────────────────────────────────


class DroneAnimationLayer:
    def __init__(
        self,
        hub_positions: Dict[str, Tuple[float, float]],
        replay_frames: List[Dict[str, Any]],
        graph=None,
        auto_replay_speed=1.0,
    ):
        self.hub_positions = hub_positions
        self.replay_frames = replay_frames
        self.graph = graph
        self.drones: Dict[str, AnimatedDrone] = {}
        self.controller = ReplayController(len(replay_frames),
                                           auto_replay_speed)
        self.last_turn = -1

        self._init_drones()
        self._apply_turn(0)

    def _init_drones(self):
        if not self.replay_frames:
            return
        frame = self.replay_frames[0]
        drones = frame.get("drones", {})
        for drone_id, data in drones.items():
            hub = data.get("zone")
            if not isinstance(hub, str):
                continue
            self.drones[drone_id] = AnimatedDrone(
                drone_id, self.hub_positions, hub
            )

    def _apply_turn(self, idx: int) -> None:
        if idx == self.last_turn or idx < 0 or idx >= len(self.replay_frames):
            return

        frame = self.replay_frames[idx]
        drones = frame.get("drones", {})

        for drone_id, data in drones.items():
            hub = data.get("zone")
            if not isinstance(hub, str):
                continue
            if drone_id not in self.drones:
                prev = hub
                if idx > 0:
                    prev_frame = self.replay_frames[idx - 1]
                    prev_d = prev_frame.get("drones", {}).get(drone_id, {})
                    prev_zone = prev_d.get("zone")
                    if isinstance(prev_zone, str):
                        prev = prev_zone
                self.drones[drone_id] = AnimatedDrone(
                    drone_id, self.hub_positions, prev
                )

            self.drones[drone_id].set_destination(hub)

        self.last_turn = idx

    def update(self, dt: float) -> None:
        self.controller.update(dt)
        self._apply_turn(self.controller.turn)

        for d in self.drones.values():
            d.update(dt)

    def handle_event(self, event) -> bool:
        return self.controller.handle_event(event)

    def draw(self, surf, camera, sw, sh, zoom, font=None):
        current_turn = self.controller.turn
        frame: Dict[str, Any] = (
            self.replay_frames[current_turn]
            if current_turn < len(self.replay_frames)
            else {}
        )
        zone_states = frame.get("zones", {})
        drone_states = frame.get("drones", {})

        occupancy: Dict[str, int] = {}
        for zone_name, zone_data in zone_states.items():
            if not isinstance(zone_data, dict):
                continue
            count = zone_data.get("count")
            if isinstance(count, int):
                occupancy[zone_name] = count

        # Draw drone sprites + ID labels
        transit_groups: Dict[Tuple[str, str], List[str]] = {}
        for drone_id, dstate in drone_states.items():
            if dstate.get("status") != "in_transit":
                continue
            conn = dstate.get("connection")
            if not isinstance(conn, dict):
                continue
            src_name = conn.get("source")
            dst_name = conn.get("target")
            if not isinstance(src_name, str) or not isinstance(dst_name, str):
                continue
            key = (src_name, dst_name)
            transit_groups.setdefault(key, []).append(drone_id)

        for drone_id, drone in self.drones.items():
            dstate = drone_states.get(drone_id, {})
            status = dstate.get("status")
            if status == "in_transit":
                conn = dstate.get("connection")
                if isinstance(conn, dict):
                    src_name = conn.get("source")
                    dst_name = conn.get("target")
                    src = self.hub_positions.get(src_name)
                    dst = self.hub_positions.get(dst_name)
                    if src and dst:
                        transit_turns = dstate.get("transit_turns", 0)
                        if not isinstance(transit_turns, int):
                            transit_turns = 0

                        transit_cost = 2
                        zone_name = dstate.get("zone")
                        if (
                            isinstance(zone_name, str)
                            and self.graph is not None
                            and zone_name in self.graph.zones
                        ):
                            transit_cost = int(
                                self.graph.zones[zone_name].move_cost()
                            )
                        transit_cost = max(1, transit_cost)

                        progress = min(
                            1.0,
                            max(0.0, (transit_turns + 0.5) / transit_cost),
                        )

                        bx = src[0] + (dst[0] - src[0]) * progress
                        by = src[1] + (dst[1] - src[1]) * progress

                        key = (src_name, dst_name)
                        group = transit_groups.get(key, [])
                        if drone_id in group and len(group) > 1:
                            idx = group.index(drone_id)
                            center = (len(group) - 1) / 2.0
                            rank = idx - center

                            dx = dst[0] - src[0]
                            dy = dst[1] - src[1]
                            length = math.hypot(dx, dy)
                            if length > 0:
                                px = -dy / length
                                py = dx / length
                                spread = 0.12
                                bx += px * rank * spread
                                by += py * rank * spread

                        drone.pos = (
                            bx,
                            by,
                        )
            drone.draw(surf, camera, sw, sh, zoom, font)

        if font is None:
            return

        # Draw live hub occupancy labels
        if self.graph is not None:
            for hub_name, (wx, wy) in self.hub_positions.items():
                sx, sy = camera.world_to_screen(wx, wy, sw, sh)
                zone = self.graph.zones.get(hub_name)
                if zone is None:
                    continue
                count = occupancy.get(hub_name, 0)
                max_d = zone.capacity if zone.capacity else 0
                color = (255, 200, 50) if count > 0 else (130, 130, 130)
                DisplayInfoHub(
                    hub_name, (int(sx), int(sy)), color, count, max_d
                ).display_hub_info(surf, font)

    def draw_overlay(self, surf, font, sw, sh):
        turn = self.controller.turn + 1
        total = self.controller.total
        state = (
            "PLAYING"
            if self.controller.state == ReplayState.PLAYING
            else "PAUSED"
        )

        info = font.render(
            f"Turn {turn}/{total} [{state}]", True, (255, 255, 255)
        )
        surf.blit(info, (10, 10))

        controls = font.render(
            "SPACE Play/Pause | ← Prev | → Next | R Restart",
            True,
            (180, 180, 180),
        )
        surf.blit(controls, (10, 35))
