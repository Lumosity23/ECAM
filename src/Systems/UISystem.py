import pygame as pg
from typing import Any


def DrawText(msg: Any, display_surface: pg.Surface, font: pg.font.Font) -> None:
    display_surface.blit(font.render(str(msg)))