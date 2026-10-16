"""
UISwitch - Animated toggle switch widget
"""

from typing import TYPE_CHECKING, Optional, Callable
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UISwitch(UIElement):
    """
    Animated toggle switch (like mobile phone settings).
    
    Features:
    - Smooth animated transition between states
    - Label text on the left
    - Visual indication of on/off state
    - Configurable colors and sizes
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        on_toggle_callback: Optional[Callable[[bool], None]] = None,
        start_state: bool = False,
        size_text: int = 50,
        text_color: tuple[int, int, int] = (255, 255, 255),
        color_on: tuple[int, int, int] = (50, 150, 50),
        color_off: tuple[int, int, int] = (150, 50, 50),
        uid: Optional[str] = None
    ):
        """
        Initialize UISwitch.
        
        Args:
            x, y: Top-left position
            text: Label text to display
            on_toggle_callback: Function called when toggled (receives new state)
            start_state: Initial state (True=on, False=off)
            size_text: Font size for the label
            text_color: RGB color for the label text
            color_on: RGB color when switch is on
            color_off: RGB color when switch is off
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "switch"
        
        # Create label text element
        uid_text = f"{uid}_text" if uid else None
        self.text_element = UIText(
            0, 0, text, size_text, text_color, uid=uid_text
        )
        
        # Switch dimensions
        self.switch_w = 100  # Width of the switch track
        self.switch_h = 50   # Height of the switch track
        self.padding = 30    # Space between text and switch
        
        # Calculate total dimensions
        text_width = self.text_element.rect.width
        total_width = text_width + self.padding + self.switch_w
        total_height = max(self.text_element.rect.h, self.switch_h)
        
        # Initialize UIElement
        super().__init__(x, y, total_width, total_height, uid)
        
        # Add text element as child
        self.add_child(self.text_element)
        
        # Position text (vertically centered)
        self.text_element.rect.midleft = (0, self.rect.h // 2)
        
        # Switch properties
        self.callback = on_toggle_callback
        self.sound = "click_default"
        
        # Colors
        self.color_on = color_on
        self.color_off = color_off
        
        # State
        self.state = start_state
        self.is_hovered = False
        
        # Animation
        self.cursor_ratio = 1.0 if start_state else 0.0  # 0.0 = off, 1.0 = on
        self.lerp_speed = 15.0  # Animation speed
        
        # Initial render
        self._render_switch()
    
    def _render_switch(self) -> None:
        """Render the switch track and thumb"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        # 1. Calculate background color by interpolating between off and on
        ratio = self.cursor_ratio
        r = int(self.color_off[0] + (self.color_on[0] - self.color_off[0]) * ratio)
        g = int(self.color_off[1] + (self.color_on[1] - self.color_off[1]) * ratio)
        b = int(self.color_off[2] + (self.color_on[2] - self.color_off[2]) * ratio)
        bg_color = (r, g, b)
        
        # 2. Add hover effect (brighten slightly)
        if self.is_hovered:
            bg_color = (
                min(255, bg_color[0] + 20),
                min(255, bg_color[1] + 20),
                min(255, bg_color[2] + 20)
            )
        
        # 3. Draw switch track (rounded rectangle)
        switch_x = self.rect.w - self.switch_w
        switch_y = (self.rect.h - self.switch_h) // 2
        
        if hasattr(self, 'panel_factory') and self.panel_factory:
            track_surface = self.panel_factory(self.switch_w, self.switch_h, bg_color)
        else:
            track_surface = pygame.Surface((self.switch_w, self.switch_h), pygame.SRCALPHA)
            # Draw rounded rect
            rect = track_surface.get_rect()
            pygame.draw.rect(track_surface, bg_color, rect, border_radius=self.switch_h//2)
        
        self.image.blit(track_surface, (switch_x, switch_y))
        
        # 4. Draw cursor (circle)
        cursor_size = self.switch_h - 8
        cursor_color = (255, 255, 255)
        
        if hasattr(self, 'panel_factory') and self.panel_factory:
            cursor_surface = self.panel_factory(cursor_size, cursor_size, cursor_color)
        else:
            cursor_surface = pygame.Surface((cursor_size, cursor_size), pygame.SRCALPHA)
            pygame.draw.circle(
                cursor_surface,
                cursor_color,
                (cursor_size // 2, cursor_size // 2),
                cursor_size // 2
            )
        
        # 5. Calculate cursor position
        min_x = switch_x + 4
        max_x = switch_x + self.switch_w - cursor_size - 4
        cursor_x = min_x + (max_x - min_x) * self.cursor_ratio
        cursor_y = switch_y + 4
        
        self.image.blit(cursor_surface, (int(cursor_x), int(cursor_y)))
    
    def update(self, dt: float) -> None:
        """Update animation state"""
        super().update(dt)
        
        # Animate cursor toward target position
        target_ratio = 1.0 if self.state else 0.0
        diff = target_ratio - self.cursor_ratio
        
        if abs(diff) > 0.01:
            self.cursor_ratio += diff * self.lerp_speed * dt
            self._render_switch()
        elif self.cursor_ratio != target_ratio:
            self.cursor_ratio = target_ratio
            self._render_switch()
    
    def set_state(self, state: bool) -> None:
        """
        Set switch state programmatically (without triggering callback).
        
        Args:
            state: True for on, False for off
        """
        if self.state != state:
            self.state = state
            # Visual update will happen in update() via lerp
    
    def get_state(self) -> bool:
        """Get current switch state"""
        return self.state
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the switch.
        
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
        
        # Update hover visuals
        if self.is_hovered != was_hovered:
            self._render_switch()
        
        # Handle mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                # Toggle state
                self.state = not self.state
                
                # Play sound (would use injected provider)
                # if self._sound_provider:
                #     self._sound_provider.play(self.sound)
                
                # Call callback
                if self.callback:
                    self.callback(self.state)
                
                return True
        
        # Let children handle event
        return super().handle_event(event)