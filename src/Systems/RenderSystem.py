import pygame as pg
from typing import TYPE_CHECKING
from .camera import Camera2D
if TYPE_CHECKING:
    from registry import Registry
    from game import Game


def RenderSystem(ecs: "Registry", camera: Camera2D, display_surface: pg.Surface, rayon: float) -> None:
    MASK_RENDER = ecs.GetMask("Transform")

    is_valid, transform = ecs.View(MASK_RENDER, "Transform")

    trans = transform[is_valid]

    x_valid = trans[:, 0].astype(int).tolist()
    y_valid = trans[:, 1].astype(int).tolist()

    for x, y in zip(x_valid, y_valid):
        sx, sy = camera.WorldToScreen(x,y)
        pg.draw.circle(display_surface, (255,0,0), (sx,sy), rayon)


def ShowGrid(game: "Game", ecs: "Registry", display_surface: pg.Surface, font: pg.font.Font) -> None:
    """ Show Grid (chunk) with count for active chunks ONLY """
    w, h = game.size
    cell = ecs.cell_size
    color = (244, 244, 244)

    # Les verticales
    for x in range(0, w, cell):
        pg.draw.line(display_surface, color, (x, 0), (x, h))
    # Les horizontales (Dessinées 1 seule fois chacune)
    for y in range(0, h, cell):
        pg.draw.line(display_surface, color, (0, y), (w, y))

    # Au lieu de parcourir l'écran, on parcourt uniquement le dictionnaire !
    for (cx, cy), entity_list in ecs.spatial_grid.items():
        count = len(entity_list)
        
        # On ne dessine le texte QUE s'il y a des entités dans ce chunk
        if count > 0:
            # Astuce Pygame : True pour l'antialiasing
            img = font.render(str(count), True, color) 
            
            # On reconvertit les coordonnées Chunk (cx, cy) en pixels pour l'écran
            pixel_x = (cx * cell) + 5
            pixel_y = (cy * cell) + 5
            
            display_surface.blit(img, (pixel_x, pixel_y))