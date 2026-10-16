"""
UISlider - Horizontal slider widget for selecting values in a range
"""

from typing import TYPE_CHECKING, Optional, Callable
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UISlider(UIElement):
    """
    Horizontal slider for selecting a value between 0.0 and 1.0.
    
    Features:
    - Visual track and draggable thumb
    - Value change callback
    - Optional value display text
    - Configurable colors and dimensions
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        initial_value: float = 0.5,
        on_change_callback: Optional[Callable[[float], None]] = None,
        uid: Optional[str] = None
    ):
        """
        Initialize UISlider.
        
        Args:
            x, y: Top-left position
            w, h: Width and height of the slider
            initial_value: Starting value between 0.0 and 1.0
            on_change_callback: Function called when value changes (receives new value)
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "slider"
        
        # Validate initial value
        self.value = max(0.0, min(1.0, float(initial_value)))
        self.callback = on_change_callback
        
        # Initialize UIElement
        super().__init__(x, y, w, h, uid)
        
        # Visual properties
        self.bar_h = h  # Height of the bar
        self.cursor_size = h  # Cursor takes full height
        
        # State
        self.is_dragging = False
        self.is_hovered = False
        
        # Value text display
        self.value_text = UIText(
            w + 20,
            h // 2,
            self._get_value_string,
            size_text=30,
            align="midleft",
            text_update=True,
            uid=f"{uid}_val" if uid else None
        )
        self.add_child(self.value_text)
        
        # Render initial state
        self._render_slider()
    
    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: resize the surface and bar to the new size"""
        self.bar_h = self.rect.h
        self.cursor_size = self.rect.h
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.value_text.rect.midleft = (self.rect.w + 20, self.rect.h // 2)
        self._render_slider()

    def _get_value_string(self) -> str:
        """Get formatted string representation of the value"""
        return f"{int(self.value * 100)}%"
    
    def _render_slider(self) -> None:
        """Render the slider track and cursor"""
        # Clear the surface
        self.image.fill((0, 0, 0, 0))
        
        # 1. Draw background bar (centered vertically)
        bar_y = (self.rect.h - self.bar_h) // 2
        bar_color = (80, 80, 80)
        if self.is_hovered:
            bar_color = (100, 100, 100)
        
        # Use panel factory if available
        if hasattr(self, 'panel_factory') and self.panel_factory:
            bar_surface = self.panel_factory(self.rect.w, self.bar_h, bar_color)
        else:
            bar_surface = pygame.Surface((self.rect.w, self.bar_h))
            bar_surface.fill(bar_color)
        
        self.image.blit(bar_surface, (0, bar_y))
        
        # 2. Draw cursor (square)
        cursor_color = (200, 200, 200)
        if self.is_dragging:
            cursor_color = (255, 255, 255)
        
        if hasattr(self, 'panel_factory') and self.panel_factory:
            cursor_surface = self.panel_factory(self.cursor_size, self.cursor_size, cursor_color)
        else:
            cursor_surface = pygame.Surface((self.cursor_size, self.cursor_size))
            cursor_surface.fill(cursor_color)
        
        # Calculate cursor position based on value
        cursor_x = (self.rect.w - self.cursor_size) * self.value
        self.image.blit(cursor_surface, (int(cursor_x), 0))
    
    def update_value_from_pos(self, mouse_x: int) -> None:
        """
        Update slider value based on mouse x position.
        
        Args:
            mouse_x: Mouse x coordinate in screen space
        """
        # Get absolute position of slider
        abs_rect = self.get_screen_rect()
        
        # Calculate relative position within the slider bar
        # Account for cursor size to prevent going out of bounds
        relative_x = mouse_x - abs_rect.x - (self.cursor_size // 2)
        max_dist = self.rect.w - self.cursor_size
        
        # Avoid division by zero
        if max_dist <= 0:
            new_value = 0.0
        else:
            new_value = max(0.0, min(1.0, relative_x / max_dist))
        
        # Update if value changed significantly
        if abs(new_value - self.value) > 0.001:
            self.value = new_value
            self._render_slider()
            if self.callback:
                self.callback(self.value)
    
    def set_value(self, value: float) -> None:
        """
        Set the slider value programmatically.
        
        Args:
            value: New value between 0.0 and 1.0
        """
        new_value = max(0.0, min(1.0, float(value)))
        if abs(new_value - self.value) > 0.001:
            self.value = new_value
            self._render_slider()
            if self.callback:
                self.callback(self.value)
    
    def get_value(self) -> float:
        """Get the current slider value"""
        return self.value
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the slider.
        
        Args:
            event: pygame Event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = abs_rect.collidepoint(mouse_pos)
        
        # Update hover state visuals
        if was_hovered != self.is_hovered:
            self._render_slider()
        
        # Handle mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_dragging = True
                self.update_value_from_pos(mouse_pos[0])
                return True
        
        # Handle mouse button up
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                self._render_slider()
                return True
        
        # Handle mouse movement while dragging
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_value_from_pos(mouse_pos[0])
                return True
        
        # Let children handle event
        return super().handle_event(event)
    
    def update(self, dt: float) -> None:
        """Update slider state"""
        super().update(dt)
        # Slider doesn't need special update logic beyond base class