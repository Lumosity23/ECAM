from __future__ import annotations

from ecam import App
from math import sin, cos, pi


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @property
    def xy(self) -> tuple[float, float]:
        """Returns the vector as a tuple"""
        return (self.x, self.y)

    @xy.setter
    def xy(self, value: tuple[float, float]):
        """Unpack from a tuple"""
        self.x, self.y = value

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> Vector2:
        return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Vector2:
        return Vector2(self.x / other, self.y / other)

    def length(self) -> float:
        """Returns the length of the vector"""
        return (self.x**2 + self.y**2) ** (1 / 2)

    def distance_to(self, vector: Vector2) -> float:
        """Returns the distance to another vector"""
        return (vector - self).length()

    def normalize(self):
        """Returns the normalized vector"""
        return self / self.length()
    
    def rotate(self, theta: float):
        """Rotate the vector with a angle"""
        x, y = self.xy
        self.x = x * cos(theta) - y * sin(theta)
        self.y = x * sin(theta) + y * cos(theta)
    
    def pos_for_screen(self, screen_size: tuple[int, int]) -> tuple[float, float]:
        """Return the position absolute for the screen"""
        return self.x + screen_size[0] / 2, self.y + screen_size[1] / 2  


class DrawLine(App):

    def __init__(self, title: str = "Test Line", width: int = 800, height: int = 600, max_fps: int = 60):
        super().__init__(title, width, height, max_fps)
        self.screen_size = width, height
        self.cell_size = 50

        #Facteur de distortion
        self.dx = 1.0
        self.dy = 0.5
        self.rot = 45
        self.theta = pi / 180 * self.rot

    def on_update(self, dt: float):
        self.on_events()
        grid = self.rotate_grid(self.make_grid(10, 10, self.cell_size), self.theta)
        for p1, p2 in grid:
            self.draw_line(p1.pos_for_screen(self.screen_size), p2.pos_for_screen(self.screen_size))

    def on_events(self):
        if self.inputs.just_pressed("ArrowRight"):
            self.dx += 0.1
        if self.inputs.just_pressed("ArrowLeft"):
            self.dx -= 0.1
        if self.inputs.just_pressed("ArrowUp"):
            self.dy += 0.1
        if self.inputs.just_pressed("ArrowDown"):
            self.dy -= 0.1
        if self.inputs.is_key_down("o"):
            self.rot -= 0.2
            self.update_theta()
        if self.inputs.is_key_down("p"):
            self.rot += 0.2
            self.update_theta()

    def rotate_grid(self, grid: list[tuple[Vector2, Vector2]], th: float) -> list[tuple[Vector2, Vector2]]:
        for point in grid:
            for p in point:
                p.rotate(th)
                p.x *= self.dx
                p.y *= self.dy
        return grid
    
    def make_grid(self, col: int, row: int, cell_size: int) -> list[tuple[Vector2, Vector2]]:
        grid = []
        grid_w = col * cell_size
        grid_h = row * cell_size
        
        for i in range(col + 1):
            x = cell_size * i - grid_w / 2
            grid.append((Vector2(x, 0 - grid_h / 2), Vector2(x, grid_h / 2)))

        for i in range(row + 1):
            y = cell_size * i - grid_h / 2
            grid.append((Vector2(-grid_w / 2, y), Vector2(grid_w / 2, y)))

        return grid

    def update_theta(self):
        self.theta = pi / 180 * self.rot

    def on_finish(self):
        print(f"Deformation en X : {self.dx}\nDeformation en Y : {self.dy}\nAngle de rotation THETA : {self.theta * 180 / pi}")

app_draw = DrawLine()
app_draw.run()

