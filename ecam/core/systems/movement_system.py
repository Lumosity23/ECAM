import numpy as np

from ..system import System


class MovementSystem(System):

    def __init__(self, registry, gravity: tuple[float, float] = (0.0, 0.0)):
        super().__init__(registry)
        self.gravity = gravity

    
    @property
    def gravity(self) -> np.ndarray:
        return self._gravity
    
    
    @gravity.setter
    def gravity(self, value) -> None:
        """Convertit automatiquement les tuples ou listes en array NumPy float32."""
        self._gravity = np.array(value, dtype=np.float32)


    def update(self, dt: float) -> None:
        """ Update the position and velocity of each entities """
        
        mask = self.registry.get_mask("Transform", "Velocity")

        is_valid, transform, velocity = self.registry.view(
            mask, "Transform", "Velocity"
        )

        if np.any(self.gravity != 0):
            if self.registry.is_component_exist("GravityScale"):
                scale = self.registry.components["GravityScale"][: self.registry.count]
                accel = self.gravity * scale[is_valid]
            else:
                accel = self.gravity
                
            velocity[is_valid] += accel * dt

        transform[is_valid] += velocity[is_valid] * dt