"""
UIProgressBar - Progress bar widget
"""

from typing import TYPE_CHECKING, Optional
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIProgressBar(UIElement):
    """
    Progress bar showing completion percentage.
    
    Features:
    - Horizontal bar showing progress from 0.0 to 1.0
    - Customizable colors for background and fill
    - Optional text display of percentage
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        value: float = 0.0,
        bg_color: tuple[int, int, int] = (80, 80, 80),
        fill_color: tuple[int, int, int] = (50, 150, 50),
        text_color: tuple[int, int, int] = (255, 255, 255),
        show_text: bool = True,
        uid: Optional[str] = None
    ):
        """
        Initialize UIProgressBar.
        
        Args:
            x, y: Top-left position
            w, h: Width and height of the progress bar
            value: Initial progress value (0.0 to 1.0)
            bg_color: Background color RGB tuple
            fill_color: Fill color RGB tuple
            text_color: Text color RGB tuple
            show_text: Whether to display percentage text
            uid: Unique identifier for layout loading
        """
        self.uid = uid
        self.type = "progress_bar"
        self._value = max(0.0, min(1.0, float(value)))
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.text_color = text_color
        self.show_text = show_text

        super().__init__(x, y, w, h, uid)
        
        self._render()

    def set_value(self, value: float) -> None:
        """Set the progress value (0.0 to 1.0)"""
        new_val = max(0.0, min(1.0, float(value)))
        if abs(new_val - self._value) > 0.001:
            self._value = new_val
            self._render()

    def get_value(self) -> float:
        """Get the current progress value"""
        return self._value

    def set_colors(self, bg: tuple, fill: tuple) -> None:
        self.bg_color = bg
        self.fill_color = fill
        self._render()

    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: resize the surface to the new size"""
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self._render()

    def _render(self) -> None:
        self.image.fill((0, 0, 0, 0))

        w, h = self.rect.width, self.rect.height

        # Background
        if hasattr(self, 'panel_factory') and self.panel_factory:
            bg_surf = self.panel_factory(w, h, self.bg_color)
        else:
            bg_surf = pygame.Surface((w, h))
            bg_surf.fill(self.bg_color)
        self.image.blit(bg_surf, (0, 0))

        # Fill
        fw = int(w * self._value)
        if fw > 0:
            if hasattr(self, 'panel_factory') and self.panel_factory:
                fill_surf = self.panel_factory(fw, h, self.fill_color)
            else:
                fill_surf = pygame.Surface((fw, h))
                fill_surf.fill(self.fill_color)
            self.image.blit(fill_surf, (0, 0))

        # Text
        if self.show_text:
            font = pygame.font.Font(None, max(12, h - 4))
            txt = font.render(f"{int(self._value * 100)}%", True, self.text_color)
            tr = txt.get_rect(center=(w // 2, h // 2))
            self.image.blit(txt, tr)

    def update(self, dt: float) -> None:
        super().update(dt)