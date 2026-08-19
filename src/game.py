import pygame as pg
import numpy as np
from registry import Registry
from Systems.camera import Camera2D
# from .manager.InputManager import InputManager
from Systems.PhysicsSystem import PhysicsSystem, CollisionSystem
from Systems.RenderSystem import RenderSystem, ShowGrid


class Game:

    def __init__(self):
        pg.init()
        pg.font.init()
        self.ecs = Registry()
        self._running = True
        self._display_surf = None
        self.clock = pg.time.Clock()
        self.debug = False
        self.is_camera = False


    def on_init(self, display_size: tuple[int, int]):
        # sizing the window
        self.size = self.width, self.height = display_size
        self.camera = Camera2D(self.width, self.height)
        self.font = pg.font.Font(size=20)
        self.rayon = 30.0

        # Init des composante de base de pygame
        self._display_surf = pg.display.set_mode(
            self.size, pg.HWSURFACE | pg.DOUBLEBUF
        )
        pg.display.set_caption("ECAM") # Entity Component Architecture Modular  ( Ca veux rien dire mais c'est drole car c'est le nom de mon ecole superieur )
                                       # ^      ^         ^            ^
        self.ecs.RegisterComponent("Transform", np.float32, (2,))
        self.ecs.RegisterComponent("Velocity", np.float32, (2,))
        self.ecs.SetSpacialGrid()
        return True


    def on_event(self, events):
        for event in events:
            if event.type == pg.QUIT:
                self._running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_d:
                self.debug = not self.debug
            elif event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                for i in range(1):
                    angle = np.random.uniform(0, 2 * np.pi)
                    speed = np.random.uniform(150, 800) 
                    vx = np.cos(angle) * speed
                    vy = np.sin(angle) * speed

                    id = self.ecs.CreateEntity(0)
                    if not self.is_camera:
                        self.camera.SetFollowEntity(self.ecs, id)
                        self.is_camera = True

                    self.ecs.AddComponent(id,
                        ("Transform", (x, y)),
                        ("Velocity", (vx, vy))
                    )
                    

    def on_loop(self, dt):
        self.ecs.UpdateSpatialGrid(100)
        self.camera.Update(self.ecs, *self.size)
        CollisionSystem(self.ecs, self.rayon)
        PhysicsSystem(self.ecs, dt, self.size, self.rayon)


    def on_render(self):
        self._display_surf.fill((10, 10, 10))  # Fond neutre
        RenderSystem(self.ecs, self.camera, self._display_surf, self.rayon)
        if self.debug:
            ShowGrid(self, self.ecs, self._display_surf, self.font)

        pg.display.flip()


    def on_cleanup(self):
        # fermeture propre de pygame
        pg.quit()


    def on_execute(self, display_size: tuple[int,int] = (1920, 1080)):
        if not self.on_init(display_size):
            self._running = False

        while self._running:

            self.on_event(pg.event.get())
            # deltaTime (temps par frame)
            dt = self.clock.tick(0) / 1000
            self.on_loop(dt)

            self.on_render()
            pg.display.set_caption(f"Nombre d'entities : {self.ecs.count} | FPS : {self.clock.get_fps():2f}")

        self.on_cleanup()
