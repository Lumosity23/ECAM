"""
UIFloatingText - Floating text for damage numbers, floating labels, etc.
"""

from typing import TYPE_CHECKING, Optional
import pygame
import math

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UIFloatingText(UIElement):
    """
    Floating text that rises and fades out over time.
    
    Features:
    - Text rises upward at configurable speed
    - Text fades out over lifetime
    - Optional drift (side-to-side movement)
    - Automatic cleanup when lifetime expires
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        lifetime: float = 2.0,
        rise_speed: float = 50.0,
        fade_start: float = 1.0,
        drift: float = 0.0,
        size_text: int = 30,
        color: tuple[int, int, int] = (255, 255, 255),
        uid: Optional[str] = None
    ):
        """
        Initialize UIFloatingText.
        
        Args:
            x, y: Starting position
            text: Text to display
            lifetime: How long to show the text (seconds)
            rise_speed: Speed at which text rises (pixels/second)
            fade_start: When to start fading (seconds before end)
            drift: Horizontal drift speed (pixels/second, positive = right)
            size_text: Font size
            color: Text color RGB tuple
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "floating_text"
        
        # Create internal UIText for rendering
        self.text_widget = UIText(
            0,
            0,
            text,
            size_text,
            color,
            uid=f"{self.uid}_text" if self.uid else None
        )
        
        # Initialize UIElement with text size
        super().__init__(
            x - self.text_widget.rect.width // 2,
            y - self.text_widget.rect.height // 2,
            self.text_widget.rect.width,
            self.text_widget.rect.height,
            uid
        )
        
        # Add text as child (centered)
        self.add_child(self.text_widget)
        self.text_widget.rect.center = (self.rect.width // 2, self.rect.height // 2)
        
        # Animation parameters
        self.lifetime = lifetime
        self.age = 0.0
        self.rise_speed = rise_speed
        self.fade_start = max(0.0, min(lifetime, fade_start))
        self.drift = drift
        
        # Start position (for drift calculation)
        self.start_x = float(self.rect.x)
        self.start_y = float(self.rect.y)
        
        # Mark as alive
        self._alive = True
    
    def update(self, dt: float) -> None:
        """
        Update the floating text animation.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if still alive, False if expired and should be removed
        """
        if not self._alive:
            return False
        
        # Update age
        self.age += dt
        
        # Check if expired
        if self.age >= self.lifetime:
            self._alive = False
            return False
        
        # Calculate progress (0.0 to 1.0)
        progress = self.age / self.lifetime
        
        # Calculate vertical position (rise)
        rise_offset = self.rise_speed * self.age
        
        # Calculate horizontal position (drift)
        drift_offset = self.drift * self.age
        
        # Apply position
        self.rect.x = int(self.start_x + drift_offset)
        self.rect.y = int(self.start_y - rise_offset)  # Negative = up
        
        # Calculate alpha for fading
        if self.age >= (self.lifetime - self.fade_start):
            # Fading out
            fade_progress = (self.age - (self.lifetime - self.fade_start)) / self.fade_start
            alpha = int(255 * (1.0 - fade_progress))
        else:
            # Fully visible
            alpha = 255
        
        # Apply alpha to the entire surface
        # We need to modify the image's alpha
        if alpha < 255:
            # Create a temporary surface with alpha
            temp_surface = self.image.copy()
            temp_surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            self.image = temp_surface
        # If alpha is 255, we keep the original image (no change needed)
        
        # Update child position to stay centered
        self.text_widget.rect.center = (self.rect.width // 2, self.rect.height // 2)
        
        return True  # Still alive
    
    def is_alive(self) -> bool:
        """Check if the floating text is still alive"""
        return self._alive
    
    def kill(self) -> None:
        """Force the floating text to die"""
        self._alive = False