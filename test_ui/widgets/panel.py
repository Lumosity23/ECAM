"""
UIPanel - Container panel widget
"""

from typing import TYPE_CHECKING, Optional
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIPanel(UIElement):
    """
    Basic UI panel/container with background and optional border.
    
    Features:
    - Background color/surface (can be injected via panel factory)
    - Optional border with configurable color and width
    - Label text capability
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: tuple[int, int, int] = (91, 110, 225),
        uid: Optional[str] = None
    ):
        """
        Initialize UIPanel.
        
        Args:
            x, y: Top-left position
            w, h: Width and height
            color: Background color RGB tuple
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "panel"
        self.color = color
        self.border_color = (255, 255, 255)  # White by default
        self.border_width = 2  # Pixels
        
        # Initialize UIElement
        super().__init__(x, y, w, h, uid)
        
        # Create background surface
        self._create_background()
        
        # Label (optional)
        self.label: Optional[any] = None
    
    def _create_background(self) -> None:
        """Create the background surface"""
        # Use injected panel factory if available, otherwise create solid color
        if hasattr(self, 'panel_factory') and self.panel_factory:
            # Panel factory expects (width, height, color) -> Surface
            factory_surface = self.panel_factory(self.rect.width, self.rect.height, self.color)
            self.image = factory_surface.copy()
        else:
            # Fallback: solid color surface
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill(self.color)
    
    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: rebuild the background for the new size"""
        self._create_background()

    def set_label(self, text: str, size_text: int = 100) -> None:
        """
        Add a text label above the panel.
        
        Args:
            text: Label text
            size_text: Font size for label
        """
        # Import here to avoid circular dependency
        from pygame_ui.widgets.text import UIText
        
        # Create label positioned above the panel
        self.label = UIText(
            self.rect.centerx,
            self.rect.top - 30,
            text,
            size_text,
            uid=f"{self.uid}_label" if self.uid else None
        )
        self.add_child(self.label)
    
    def set_color(self, color: tuple[int, int, int]) -> None:
        """Change the panel background color"""
        self.color = color
        self._create_background()
    
    def set_border(self, color: tuple[int, int, int], width: int = 2) -> None:
        """
        Set border properties.
        
        Args:
            color: Border color RGB tuple
            width: Border width in pixels
        """
        self.border_color = color
        self.border_width = width
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the panel and its children.
        
        Args:
            surface: Target pygame Surface
        """
        if not self.visible:
            return
        
        # Draw background
        super().draw(surface)
        
        # Draw border (if not in debug mode, or always draw border?)
        # Following original: border drawn in debug zone comment
        if not self.debug and self.border_width > 0:
            abs_rect = self.get_screen_rect()
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)