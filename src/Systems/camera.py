import pygame as pg
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from registry import Registry


class Camera2D:
    def __init__(self, screen_width: int, screen_height: int):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.target_entity: "Registry.UINT32" = 0
        self.screen_width = screen_width
        self.screen_height = screen_height


    def SetFollowEntity(self, ecs: "Registry", id: "Registry.UINT32") -> None:
        """ Focus sur une entity """
        self.target_entity = id
        self.offset_x, self.offset_y = ecs.components["Transform"][id]


    def Update(self, ecs: "Registry", map_width: int, map_height: int):
        """Met à jour la position de la caméra pour centrer la cible, avec verrouillage aux bords"""
        # On recupere la position de notre "Follow Entity"
        self.offset_x, self.offset_y = ecs.components["Transform"][self.target_entity]
        
        # On calcule la position idéale (pour centrer la cible à l'écran)
        ideal_x = self.offset_x - (self.screen_width / 2.0)
        ideal_y = self.offset_y - (self.screen_height / 2.0)

        # Le CAMERA CLAMPING (Le secret de Celeste !)
        # On empêche l'offset_x d'aller en dessous de 0 (bord gauche)
        # Et on l'empêche de dépasser (map_width - screen_width) (bord droit)
        self.offset_x = max(0.0, min(ideal_x, map_width - self.screen_width))
        self.offset_y = max(0.0, min(ideal_y, map_height - self.screen_height))


    def WorldToScreen(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Convertit une position du monde en position sur l'écran"""
        screen_x = world_x - self.offset_x
        screen_y = world_y - self.offset_y
        return screen_x, screen_y