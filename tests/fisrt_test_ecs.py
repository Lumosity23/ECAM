import numpy as np
import pygame as pg
from random import uniform
import time
from typing import Any


UINT8  = np.uint8
UINT32 = np.uint32
UINT64 = np.uint64

FLOAT16  = np.float16
FLOAT32  = np.float32
FLOAT128 = np.float128

MASK_NONE  = 0
MASK_POS   = 1 << 0
MASK_VELO  = 1 << 1
MASK_SHAPE = 1 << 2


class registry:

    MAX_ENTITIES = 10000


    def _GetArrayZeros(self, type, shape: tuple = ()) -> np.ndarray :
        final_shape = (self.MAX_ENTITIES, *shape)
        return np.zeros(final_shape, dtype=type)
    

    def _UpdateSignature(self, id: UINT32, MASK: int):
        self.signatures[id] |= MASK


    def _Swap2End(self, id: UINT32, array: np.ndarray):
        last_id = self.count - 1
        array[id] = array[last_id]


    def __init__(self):
        self.count = 0
        self.signatures = self._GetArrayZeros(UINT32)
        self.components: dict[str, np.ndarray] = {}
        self.masks: dict[str, int] = {}


    def RegisterComponent(self, name: str, dtype: np.dtype, shape: tuple = ()):
        """ Register a new component for ce ecs """
        array_component = self._GetArrayZeros(dtype, shape)
        mask_component = 1 << len(self.masks)

        self.components[name] = array_component
        self.masks[name] = mask_component


    def CreateEntity(self, entity_signature) -> int:
        """ Create a new entity """
        if self.count >= self.MAX_ENTITIES: return -1

        id = self.count
        self.signatures[id] = entity_signature
        self.count += 1
        return id
    

    def AddComponent(self, id: UINT32, *bundle_component_n_value: tuple[str, Any]) -> None:
        for name, value in bundle_component_n_value:
            if name in self.components:
                self.components[name][id] = value
                self._UpdateSignature(id, self.masks[name])

            # Erreur non bloquante
            else : print(f"[ERROR] Component '{name}' does not exist!")


    def Query(self, mask: int) -> np.ndarray:
        active_signatures = self.signatures[:self.count]
        return ( active_signatures & mask ) == mask
    
    
    def View(self, mask: int, *component_name: str) -> tuple[np.ndarray]:
        is_valid = self.Query(mask)
        arrays = tuple(self.components[name][:self.count] for name in component_name)
        return (is_valid, *arrays)


    def DestroyEntity(self, id: int) -> None:
        if id < 0 or id >= self.count:
            return 

        for array in self.components.values():
            self._Swap2End(id, array)
        
        self._Swap2End(id, self.signatures)

        self.count -= 1


def PhysicsSystem(ecs: registry, dt: float, screen_width: int = 1920, screen_height: int = 1080) -> None:
    MASK_PHYSICS = MASK_POS | MASK_VELO

    is_valid, pos_x, pos_y, vel_x, vel_y = ecs.View(MASK_PHYSICS, "pos_x", "pos_y", "vel_x", "vel_y")
    
    pos_x[is_valid] += vel_x[is_valid] * dt
    pos_y[is_valid] += vel_y[is_valid] * dt

    


def RenderSystem(ecs: registry, surface: pg.Surface) -> None:
    surface.fill("black")

    is_valid, pos_x, pos_y = ecs.View(MASK_POS, "pos_x", "pos_y")

    valid_x = pos_x[is_valid].astype(float).tolist()
    valid_y = pos_y[is_valid].astype(float).tolist()

    for x, y in zip(valid_x, valid_y):
        pg.draw.circle(surface, (255,0,0), (x, y), 10.0)


def main():
    
    # Pygame Stuff
    pg.init()
    pg.font.init()

    font = pg.font.SysFont("Fira Mono", 30)

    window_size = 1920, 1080
    _display_surf = pg.display.set_mode(
        window_size, pg.HWSURFACE | pg.DOUBLEBUF
    )
    clock = pg.time.Clock()
    is_running = True

    # ECS stuff
    ecs = registry()
    ecs.RegisterComponent("pos_x", FLOAT32)
    ecs.RegisterComponent("pos_y", FLOAT32)
    ecs.RegisterComponent("vel_x", FLOAT32)
    ecs.RegisterComponent("vel_y", FLOAT32)

    while is_running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_running = False
            elif event.type == pg.MOUSEBUTTONDOWN and ecs.count < 10000:
                x, y = pg.mouse.get_pos()
                for _ in range(1000):
                    id = ecs.CreateEntity(0)
                    
                    # ecs.AddShape(id, surface_cercle)

        dt = clock.tick(0) / 1000
        PhysicsSystem(ecs, dt)

        start_time = time.perf_counter()
        RenderSystem(ecs, _display_surf)
        logic_time = (time.perf_counter() - start_time) * 1000 # En millisecondes

        # Draw Text on screen
        fps = clock.get_fps()
        pg.display.set_caption(f"POO Benchmark - FPS: {int(fps)} | Temps Logique: {logic_time:.2f} ms | nmb entities : {ecs.count}")
        
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
