"""
UIRange - World-space range indicator widget
"""

from typing import TYPE_CHECKING, Optional, Callable
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIRange(UIElement):
    """
    Range indicator showing distance or range in world space.
    
    Features:
    - Can operate in screen space or world space
    - In world space, accepts camera offset for positioning
    - Shows a circular range indicator
    - Configurable colors and ranges
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 50,
        color: tuple[int, int, int] = (100, 100, 255, 100),
        inner_color: tuple[int, int, int] = (100, 100, 255, 200),
        value: float = 0.5,  # 0.0 to 1.0 representing % of max range
        max_range: float = 100.0,
        uid: Optional[str] = None
    ):
        """
        Initialize UIRange.
        
        Args:
            x, y: Center position (in screen space by default)
            radius,            uid: Unique identifier for layout loading
            uid: Unique identifier for loading layout
        """
        # Store parameters
        self.uid = uid
        self.type = "range"
        
        self.radius = radius
        self.color = color  # Outer ring color (with alpha)
        self.inner_color = inner_color  # Inner fill color (with alpha)
        self.value = max(0.0, min(1.0, float(value)))  # % of max range
        self.max_range = max_range
        
        # World space mode - when True, position is adjusted by camera offset
        self.world_space = False
        
        # Initialize UIElement (diameter for width/height)
        diameter = radius * 2
        super().__init__(x - radius, y - radius, diameter, diameter, uid)
        
        # Create initial surface
        self._create_surfaces()
    
    def _create_surfaces(self) -> None:
        """Create the range indicator surfaces"""
        diameter = self.radius * 2
        # Create surface with alpha channel
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        
        # Clear to transparent
        self.image.fill((0, 0, 0, 0))
        
        # Draw outer ring (empty circle)
        ring_width = max(2, self.radius // 10)
        pygame.draw.circle(
            self.image,
            self.color,
            (self.radius, self.radius),
            self.radius,
            ring_width
        )
        
        # Draw inner fill based on value
        if self.value > 0:
            # Calculate radius for the filled portion
            fill_radius = int(self.radius * self.value)
            if fill_radius > 0:
                pygame.draw.circle(
                    self.image,
                    self.inner_color,
                    (self.radius, self.radius),
                    fill_radius
                )
    
    def set_value(self, value: float) -> None:
        """
        Set the range value.
        
        Args:
            value: New value (0.0 to 1.0 representing % of max range)
        """
        new_value = max(0.0, min(1.0, float(value)))
        if abs(new_value - self.value) > 0.001:
            self.value = new_value
            self._create_surfaces()
    
    def get_value(self) -> float:
        """Get the current range value (0.0 to 1.0)"""
        return self.value
    
    def set_range(self, max_range: float) -> None:
        """Set the maximum range value"""
        self.max_range = max_range
    
    def get_range_value(self) -> float:
        """Get the actual range value (0.0 to max_range)"""
        return self.value * self.max_range
    
    def set_world_space(self, enabled: bool = True) -> None:
        """
        Enable or disable world space mode.
        
        In world space mode, the widget's position is adjusted by a camera offset
        provided during drawing.
        
        Args:
            enabled: True to enable world space mode
        """
        self.world_space = enabled
    
    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """
        Draw the range indicator.
        
        Args:
            surface: Target pygame Surface
            camera_offset: (x, y) offset to apply for world space mode
        """
        if not self.visible:
            return
        
        # Calculate draw position
        base_pos = self.get_screen_rect().topleft
        
        if self.world_space:
            # Apply camera offset
            draw_pos = (
                base_pos[0] + camera_offset[0],
                base_pos[1] + camera_offset[1]
            )
        else:
            draw_pos = base_pos
        
        # Draw the image at the calculated position
        surface.blit(self.image, draw_pos)
        
        # Draw children (if any)
        super().draw(surface)
    
    def update(self, dt: float) -> None:
        """Update - range indicator doesn't need special update logic"""
        super().update(dt)