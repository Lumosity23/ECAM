"""
UIDot - Simple colored dot indicator
"""

from typing import TYPE_CHECKING, Optional
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIDot(UIElement):
    """
    Simple circular dot indicator.
    
    Features:
    - Configurable color and radius
    - Solid circle rendered as pygame Surface
    - Can be used as status indicator, cursor, etc.
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 5,
        color: tuple[int, int, int] = (255, 255, 255),
        uid: Optional[str] = None
    ):
        """
        Initialize UIDot.
        
        Args:
            x, y: Center position of the dot
            radius: Radius of the dot in pixels
            color: RGB color tuple
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "dot"
        self.radius = radius
        self.color = color
        
        # Calculate size (diameter)
        diameter = radius * 2
        
        # Initialize UIElement
        super().__init__(x - radius, y - radius, diameter, diameter, uid)
        
        # Create the dot surface
        self._create_dot_surface()
        
        # Set rect to center at (x, y) if not loaded from layout
        if not self.cfg_loaded:
            self.rect.center = (x, y)
    
    def _create_dot_surface(self) -> None:
        """Create the circular dot surface"""
        diameter = self.radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        
        # Draw circle centered in the surface
        pygame.draw.circle(
            surface,
            self.color,
            (self.radius, self.radius),
            self.radius
        )
        
        self.image = surface
    
    def set_color(self, color: tuple[int, int, int]) -> None:
        """Change the dot color"""
        self.color = color
        self._create_dot_surface()
    
    def set_radius(self, radius: int) -> None:
        """Change the dot radius"""
        self.radius = radius
        diameter = radius * 2
        # Resize the rect
        old_center = self.rect.center
        self.rect.width = diameter
        self.rect.height = diameter
        self.rect.center = old_center
        
        # Recreate the surface
        self._create_dot_surface()
    
    def update(self, dt: float) -> None:
        """Update - dots don't need special update logic"""
        super().update(dt)