"""
UIIcon - Icon/sprite display widget
"""

from typing import TYPE_CHECKING, Optional
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIIcon(UIElement):
    """
    Icon/widget for displaying sprites or images.
    
    Features:
    - Displays a pygame Surface (sprite/icon)
    - Can be tinted with a color
    - Size can be specified or auto-sized from image
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        image: pygame.Surface,
        tint_color: Optional[tuple[int, int, int]] = None,
        uid: Optional[str] = None
    ):
        """
        Initialize UIIcon.
        
        Args:
            x, y: Top-left position
            image: pygame Surface to display
            tint_color: Optional RGB tint to apply (None for no tint)
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "icon"
        self.tint_color = tint_color
        
        # Store original image
        self.original_image = image
        
        # Initialize UIElement with image dimensions
        super().__init__(x, y, image.get_width(), image.get_height(), uid)
        
        # Apply tint if specified
        if self.tint_color:
            self._apply_tint()
        else:
            self.image = self.original_image.copy()
            
        # Set rect based on alignment (if not loaded from layout)
        if not self.cfg_loaded:
            # Default topleft alignment for consistency
            self.rect.x = x
            self.rect.y = y
    
    def _apply_tint(self) -> None:
        """Apply tint color to the image"""
        # Create a copy to avoid modifying original
        tinted = self.original_image.copy()
        
        # Create a surface filled with the tint color
        tint_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*self.tint_color, 128))  # 50% opacity tint
        
        # Blend the tint onto the image
        tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = tinted
    
    def set_image(self, image: pygame.Surface) -> None:
        """Change the displayed image"""
        self.original_image = image
        # Resize to match new image
        self.rect.width = image.get_width()
        self.rect.height = image.get_height()
        
        # Apply tint if needed
        if self.tint_color:
            self._apply_tint()
        else:
            self.image = self.original_image.copy()
    
    def set_tint(self, color: Optional[tuple[int, int, int]]) -> None:
        """Set or change the tint color"""
        self.tint_color = color
        if color:
            self._apply_tint()
        else:
            self.image = self.original_image.copy()
    
    def update(self, dt: float) -> None:
        """Update - icons don't need special update logic"""
        super().update(dt)