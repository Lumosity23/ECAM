"""
UIStat - Stat display widget (label + value)
"""

from typing import TYPE_CHECKING, Optional, Callable, Union
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UIStat(UIElement):
    """
    Stat display showing a label and a value.
    
    Features:
    - Label text (static)
    - Value text (can be static or dynamic via callback)
    - Automatic layout (label left, value right)
    - Optional value formatting
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        label: str,
        value_or_callback: Union[str, Callable[[], str]] = "",
        label_size: int = 30,
        value_size: int = 30,
        label_color: tuple[int, int, int] = (200, 200, 200),
        value_color: tuple[int, int, int] = (255, 255, 255),
        value_update: bool = False,
        uid: Optional[str] = None
    ):
        """
        Initialize UIStat.
        
        Args:
            x, y: Top-left position
            label: Static label text
            value_or_callback: Value string OR callable that returns string
            label_size: Font size for label
            value_size: Font size for value
            label_color: Label text color RGB tuple
            value_color: Value text color RGB tuple
            value_update: If True, treat value_or_callback as a callable for dynamic updates
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "stat"
        
        # Initialize UIElement with temporary size (will be updated)
        super().__init__(x, y, 0, 0, uid)
        
        # Create label
        self.label_text = UIText(
            0,
            0,
            label,
            label_size,
            label_color,
            uid=f"{self.uid}_label" if self.uid else None
        )
        
        # Create value text (static or dynamic)
        if value_update and callable(value_or_callback):
            self.value_text = UIText(
                0,
                0,
                value_or_callback,
                value_size,
                value_color,
                text_update=True,
                uid=f"{self.uid}_value" if self.uid else None
            )
        else:
            self.value_text = UIText(
                0,
                0,
                str(value_or_callback),
                value_size,
                value_color,
                uid=f"{self.uid}_value" if self.uid else None
            )
        
        # Add both as children
        self.add_child(self.label_text)
        self.add_child(self.value_text)
        
        # Initial layout
        self._layout_components()
    
    def _layout_components(self) -> None:
        """Layout label and value side by side"""
        if not self.children:
            return
        
        # Position label at left
        self.label_text.rect.x = 0
        self.label_text.rect.y = (self.rect.height - self.label_text.rect.height) // 2
        
        # Position value at right
        self.value_text.rect.x = self.rect.width - self.value_text.rect.width
        self.value_text.rect.y = (self.rect.height - self.value_text.rect.height) // 2
        
        # Update size to fit both
        total_width = self.label_text.rect.width + self.value_text.rect.width + 10  # 10px gap
        total_height = max(self.label_text.rect.height, self.value_text.rect.height)
        
        # Only update size if we're not constrained by layout
        if not self.cfg_loaded:
            self.rect.width = max(self.rect.width, total_width + 20)  # 20px padding
            self.rect.height = max(self.rect.height, total_height + 20)  # 20px padding
            
            # Re-position with padding
            padding_x = (self.rect.width - (self.label_text.rect.width + self.value_text.rect.width + 10)) // 2
            padding_y = (self.rect.height - max(self.label_text.rect.height, self.value_text.rect.height)) // 2
            
            self.label_text.rect.x = padding_x
            self.label_text.rect.y = padding_y + (self.rect.height - 2*padding_y - self.label_text.rect.height) // 2
            
            self.value_text.rect.x = padding_x + self.label_text.rect.width + 10
            self.value_text.rect.y = padding_y + (self.rect.height - 2*padding_y - self.value_text.rect.height) // 2
    
    def set_label(self, label: str) -> None:
        """Update the label text"""
        self.label_text.set_text(label)
        self._layout_components()
    
    def set_value(self, value: Union[str, Callable[[], str]]) -> None:
        """Update the value (can be string or callable for dynamic updates)"""
        if callable(value):
            # Convert to dynamic text
            self.value_text.set_callback(value)
        else:
            # Static text
            self.value_text.set_text(str(value))
            # Remove callback if it was dynamic
            self.value_text.text_update = False
            self.value_text.text_callback = None
        
        self._layout_components()
    
    def get_value(self) -> str:
        """Get the current value string"""
        if self.value_text.text_update and self.value_text.text_callback:
            return self.value_text.text_callback()
        else:
            return self.value_text.static_text
    
    def update(self, dt: float) -> None:
        """Update - let children handle their own updates"""
        super().update(dt)
        # Re-layout if size changed due to text updates
        self._layout_components()