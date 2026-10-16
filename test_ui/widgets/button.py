"""
UIButton - Clickable button widget
"""

from typing import TYPE_CHECKING, Optional, Callable
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UIButton(UIElement):
    """
    Clickable button widget with hover/press states and optional toggle behavior.
    
    Features:
    - Visual feedback for idle/hover/pressed states
    - Optional toggle mode (like a checkbox)
    - Text label with automatic sizing
    - Configurable colors and border radius
    - Click sound provider injection (optional)
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        on_click_callback: Optional[Callable[[], None]] = None,
        color: tuple[int, int, int] = (0, 0, 0),
        size_text: int = 50,
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_radius: int = 15,
        uid: Optional[str] = None,
        w: Optional[int] = None,
        h: Optional[int] = None
    ):
        """
        Initialize UIButton.

        Args:
            x, y: Top-left position
            text: Button label text
            on_click_callback: Function to call when clicked
            color: Base color RGB tuple
            size_text: Font size for text
            text_color: Text color RGB tuple
            border_radius: Corner radius in pixels
            uid: Unique identifier for layout loading
            w, h: Fixed width/height in pixels. If omitted, the size is
                computed from the label plus padding. The label is always centered.
        """
        # Store parameters
        self.uid = uid
        self.type = "button"
        self.fixed_width = w
        self.fixed_height = h

        # Create text label first to get its dimensions
        text_uid = f"{uid}_text" if uid else None
        self.text = UIText(0, 0, text, size_text, text_color, uid=text_uid)

        # Initialize UIElement with the size resolved from text or explicit w/h
        button_width, button_height = self._compute_size()
        super().__init__(x, y, button_width, button_height, uid)

        # Add text as child and position it
        self.add_child(self.text)
        # A size from the layout file is authoritative: keep it as the fixed size
        if self.cfg_loaded:
            self.fixed_width, self.fixed_height = self.rect.size
        self._layout_text()

        # Visual properties
        self.border_radius = border_radius
        self.callback = on_click_callback
        self.sound = "click_default"  # Default sound name

        # State management
        self.current_color = color
        self.is_toggle = False
        self.toggle_state = False
        self.toggle_config = {}

        # Visual state
        self.shape: dict[str, pygame.Surface] = {}
        self.state = "IDLE"  # IDLE, HOVER, PRESSED

        # Initialize colors and shapes
        self.set_color(color)

    def _compute_size(self) -> tuple[int, int]:
        """
        Return the button size: fixed w/h if given, otherwise text size plus padding.
        """
        # UIText keeps its rect at 0x0, so the real label size comes from its image
        text_w, text_h = self.text.image.get_size()
        width = self.fixed_width if self.fixed_width is not None else text_w + 40
        height = self.fixed_height if self.fixed_height is not None else text_h + 20
        return width, height

    def _layout_text(self) -> None:
        """Resize the button to its current size rules and center the label inside it."""
        self.rect.width, self.rect.height = self._compute_size()
        text_w, text_h = self.text.image.get_size()
        self.text.rect.topleft = (
            (self.rect.width - text_w) // 2,
            (self.rect.height - text_h) // 2
        )

    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: its size becomes the fixed size"""
        self.fixed_width, self.fixed_height = self.rect.size
        self._layout_text()
        self.set_color(self.current_color)

    def set_size(self, w: Optional[int], h: Optional[int]) -> None:
        """
        Set a fixed size for the button (None on an axis restores auto-sizing on that axis).

        Args:
            w: Width in pixels, or None to size from the text
            h: Height in pixels, or None to size from the text
        """
        self.fixed_width = w
        self.fixed_height = h
        self._layout_text()
        self.set_color(self.current_color)

    def set_color(self, color: tuple[int, int, int]) -> None:
        """
        Set the button's base color and regenerate state images.
        
        Args:
            color: New base color RGB tuple
        """
        self.current_color = color
        
        # Calculate hover and pressed colors based on brightness
        r, g, b = color
        # Calculate perceived luminance
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        
        if l > 128:  # Light color
            # Darken for hover, even darker for pressed
            color_hover = (
                max(0, int(r * 0.9)),
                max(0, int(g * 0.9)),
                max(0, int(b * 0.9))
            )
            color_pressed = (
                max(0, int(r * 0.8)),
                max(0, int(g * 0.8)),
                max(0, int(b * 0.8))
            )
        else:  # Dark color
            # Lighten for hover, even lighter for pressed
            color_hover = (
                min(255, int(r * 1.1)),
                min(255, int(g * 1.1)),
                min(255, int(b * 1.1))
            )
            color_pressed = (
                min(255, int(r * 1.2)),
                min(255, int(g * 1.2)),
                min(255, int(b * 1.2))
            )
        
        # Create surfaces for each state
        state_colors = {
            "IDLE": color,
            "HOVER": color_hover,
            "PRESSED": color_pressed
        }
        
        self.shape = self._make_shape_from_colors(state_colors)
        
        # Set initial image
        self.image = self.shape[self.state]
    
    def _make_shape_from_colors(self, color_dict: dict[str, tuple[int, int, int]]) -> dict[str, pygame.Surface]:
        """
        Create pygame surfaces for each button state using panel factory.
        
        Args:
            color_dict: Mapping of state names to RGB colors
            
        Returns:
            Dictionary mapping state names to pygame Surfaces
        """
        result = {}
        
        # Use injected panel factory if available
        if hasattr(self, 'panel_factory') and self.panel_factory:
            for state, color in color_dict.items():
                surface = self.panel_factory(
                    self.rect.width,
                    self.rect.height,
                    color
                )
                result[state] = surface
        else:
            # Fallback: draw rectangles with pygame
            for state, color in color_dict.items():
                surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                # Draw rounded rect
                if self.border_radius > 0:
                    pygame.draw.rect(
                        surface,
                        color,
                        surface.get_rect(),
                        border_radius=self.border_radius
                    )
                else:
                    pygame.draw.rect(surface, color, surface.get_rect())
                result[state] = surface
        
        return result
    
    def set_sound(self, sound: str) -> None:
        """Set the sound effect name for clicks"""
        self.sound = sound
    
    def set_text(self, text: str) -> None:
        """
        Update button text and resize button accordingly.
        
        Args:
            text: New button text
        """
        self.text.set_text(text)
        # Recalculate size (fixed w/h are kept) and reposition text
        self._layout_text()
        # Regenerate button surfaces with new size
        self.set_color(self.current_color)
    
    def setup_toggle(
        self,
        text_off: str,
        color_off: tuple[int, int, int],
        text_on: str,
        color_on: tuple[int, int, int],
        start_state: bool = False
    ) -> None:
        """
        Configure button as a two-state toggle switch.
        
        Args:
            text_off: Text when toggle is off
            color_off: Color when toggle is off
            text_on: Text when toggle is on
            color_on: Color when toggle is on
            start_state: Initial toggle state
        """
        self.is_toggle = True
        self.toggle_config = {
            False: {"text": text_off, "color": color_off},
            True: {"text": text_on, "color": color_on}
        }
        self.set_toggle_state(start_state)
    
    def update_toggle_visuals(self) -> None:
        """Update button appearance based on toggle state"""
        if not self.is_toggle:
            return
        cfg = self.toggle_config[self.toggle_state]
        self.text.set_text(cfg["text"])
        # Resize button to fit new text (fixed w/h are kept) and reposition text
        self._layout_text()
        # Update colors
        self.set_color(cfg["color"])
    
    def set_toggle_state(self, state: bool) -> None:
        """
        Set toggle state programmatically (without triggering callback).
        
        Args:
            state: True for on, False for off
        """
        if self.toggle_state != state or not self.shape:
            self.toggle_state = state
            self.update_toggle_visuals()
    
    def _play_click_sound(self) -> None:
        """Play click sound using injected sound provider"""
        # This would be implemented with a sound provider injection
        # For now, it's a placeholder - the original used event bus
        pass
    
    def render(self) -> None:
        """Update the button's visual appearance based on state"""
        # Choose the correct surface based on current state
        if self.state in self.shape:
            self.image = self.shape[self.state]
        # Fallback to IDLE state if somehow missing
        elif "IDLE" in self.shape:
            self.image = self.shape["IDLE"]
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the button.
        
        Args:
            event: pygame Event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        abs_rect = self.get_screen_rect()
        # Use the position carried by the event (mouse events have one), not the live cursor
        mouse_pos = getattr(event, "pos", None) or pygame.mouse.get_pos()
        is_hovered = abs_rect.collidepoint(mouse_pos)
        
        old_state = self.state
        
        # Handle mouse movement
        if event.type == pygame.MOUSEMOTION:
            self.state = "HOVER" if is_hovered else "IDLE"
        
        # Handle mouse button down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_hovered and event.button == 1:  # Left click
                self.state = "PRESSED"
                
                # Handle toggle behavior
                if self.is_toggle:
                    self.toggle_state = not self.toggle_state
                    self.update_toggle_visuals()
                
                # Execute callback
                if self.callback:
                    # Play sound (would use injected provider)
                    self._play_click_sound()
                    self.callback()
                
                # Force visual update
                self.render()
                return True
        
        # Handle mouse button up
        elif event.type == pygame.MOUSEBUTTONUP:
            if is_hovered and event.button == 1:
                self.state = "HOVER" if is_hovered else "IDLE"
            else:
                self.state = "IDLE"
        
        # Update visual if state changed
        if self.state != old_state:
            self.render()
        
        return False  # Let children try to handle event too
    
    def update(self, dt: float) -> None:
        """Update button state"""
        super().update(dt)
        # Button doesn't need special update logic beyond base class