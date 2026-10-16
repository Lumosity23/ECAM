import numpy as np

from ..system import System


class BoundarySystem(System):

    def __init__(
        self,
        registry,
        bounds: tuple[float, float, float, float],
        restitution: float = 0.8,  # Facteur de rebond (0.8 = 80%)
        mode: str = "bounce",  # "bounce" pour rebondir, "wrap" pour se téléporter
    ):
        super().__init__(registry)
        self.min_x, self.min_y, self.max_x, self.max_y = bounds
        self.restitution = restitution
        self.mode = mode

    def update(self, dt: float) -> None:
        count = self.registry.count
        if count == 0:
            return

        # 1. On récupère les tableaux Transform et Velocity
        mask = self.registry.get_mask("Transform")
        is_valid, transform = self.registry.view(mask, "Transform")

        x = transform[:count, 0]
        y = transform[:count, 1]

        # Demi-taille (si BoxCollider existe, sinon 0)
        if "BoxCollider" in self.registry.components:
            box = self.registry.components["BoxCollider"][:count]
            hw = box[:, 0]
            hh = box[:, 1]
        else:
            hw, hh = 0.0, 0.0

        # --------------------------------------------------------------
        # OPTION A : MODE WRAP (Téléportation de l'autre côté de l'écran)
        # --------------------------------------------------------------
        if self.mode == "wrap":
            # Si ça dépasse à droite -> téléporté à gauche
            x[x > self.max_x] = self.min_x
            # Si ça dépasse à gauche -> téléporté à droite
            x[x < self.min_x] = self.max_x
            # Si ça dépasse en bas -> téléporté en haut
            y[y > self.max_y] = self.min_y
            # Si ça dépasse en haut -> téléporté en bas
            y[y < self.min_y] = self.max_y
            return

        # --------------------------------------------------------------
        # OPTION B : MODE BOUNCE (Rebond avec amorti)
        # --------------------------------------------------------------
        hit_left = x - hw < self.min_x
        hit_right = x + hw > self.max_x
        hit_top = y - hh < self.min_y
        hit_bottom = y + hh > self.max_y

        # Clamping de position (pour ne pas traverser le mur)
        x[hit_left] = self.min_x + (hw[hit_left] if hasattr(hw, "__len__") else hw)
        x[hit_right] = self.max_x - (hw[hit_right] if hasattr(hw, "__len__") else hw)
        y[hit_top] = self.min_y + (hh[hit_top] if hasattr(hh, "__len__") else hh)
        y[hit_bottom] = self.max_y - (hh[hit_bottom] if hasattr(hh, "__len__") else hh)

        # Réflexion de vitesse
        if "Velocity" in self.registry.components:
            velocity = self.registry.components["Velocity"][:count]
            vel_x = velocity[:, 0]
            vel_y = velocity[:, 1]

            vel_x[hit_left | hit_right] *= -self.restitution
            vel_y[hit_top | hit_bottom] *= -self.restitution