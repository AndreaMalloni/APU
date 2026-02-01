class Camera:
    """Camera for rendering scenes"""

    def __init__(self, position: tuple[float, float] = (0, 0), zoom: float = 1.0):
        self.position = list(position)
        self.zoom = zoom
        self.target_position = list(position)
        self.target_zoom = zoom
        self.smooth_factor = 0.1

    def follow(self, target: tuple[float, float], dt: float) -> None:
        """Follows a target with smooth movement"""
        self.target_position = list(target)
        self.position[0] += (self.target_position[0] - self.position[0]) * self.smooth_factor * dt
        self.position[1] += (self.target_position[1] - self.position[1]) * self.smooth_factor * dt

    def world_to_screen(self, world_pos: tuple[float, float]) -> tuple[float, float]:
        """Converts world coordinates to screen coordinates"""
        return (
            (world_pos[0] - self.position[0]) * self.zoom,
            (world_pos[1] - self.position[1]) * self.zoom,
        )

    def screen_to_world(self, screen_pos: tuple[float, float]) -> tuple[float, float]:
        """Converts screen coordinates to world coordinates"""
        return (
            screen_pos[0] / self.zoom + self.position[0],
            screen_pos[1] / self.zoom + self.position[1],
        )
