"""
UIUpgradeBoard - Board of purchasable upgrades widget
"""

from typing import TYPE_CHECKING, Optional, Callable, Dict, Any
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText
from pygame_ui.widgets.button import UIButton

if TYPE_CHECKING:
    import pygame.font


class UIUpgradeBoard(UIElement):
    """
    Upgrade board/display for showing available upgrades and costs.
    
    Features:
    - Displays player resources (wallet, currency, etc.)
    - Shows upgrade options with costs
    - Value provider injection for dynamic values (replaces RPC calls)
    - Click-to-purchase functionality
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str = "Upgrades",
        title_size: int = 40,
        value_provider: Optional[Callable[[str], Any]] = None,
        uid: Optional[str] = None
    ):
        """
        Initialize UIUpgradeBoard.
        
        Args:
            x, y: Top-left position
            w, h: Width and height
            title: Panel title text
            title_size: Font size for title
            value_provider: Function that takes a key string and returns a value
                           (replaces the old RPC mechanism)
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "upgrade_board"
        
        # Initialize UIElement
        super().__init__(x, y, w, h, uid)
        
        # Create title
        self.title_text = UIText(
            w // 2,
            20,
            title,
            title_size,
            (255, 255, 255),
            align="center",
            uid=f"{self.uid}_title" if self.uid else None
        )
        self.add_child(self.title_text)
        
        # Value provider for getting game values (replaces RPC)
        self.value_provider = value_provider
        
        # Store for upgrade buttons and displays
        self.upgrade_buttons: dict[str, UIButton] = {}
        self.value_displays: dict[str, UIText] = {}
        
        # Background
        self.bg_color = (40, 40, 60)
        self._create_background()
    
    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: rebuild background and re-center the title"""
        self._create_background()
        self.title_text.rect.center = (self.rect.width // 2, 20)

    def _create_background(self) -> None:
        """Create the background surface"""
        if hasattr(self, 'panel_factory') and self.panel_factory:
            self.image = self.panel_factory(self.rect.width, self.rect.height, self.bg_color)
        else:
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill(self.bg_color)
    
    def set_value_provider(self, provider: Callable[[str], Any]) -> None:
        """
        Set the value provider function.
        
        Args:
            provider: Function that takes a key (string) and returns a value
                     e.g., lambda key: player.wallet.get(key, 0)
        """
        self.value_provider = provider
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value using the value provider.
        
        Args:
            key: The key to look up
            default: Default value if provider returns None or fails
            
        Returns:
            The value from the provider, or default
        """
        if self.value_provider:
            try:
                return self.value_provider(key)
            except Exception:
                return default
        return default
    
    def add_value_display(
        self,
        key: str,
        label: str,
        x: int,
        y: int,
        label_size: int = 24,
        value_size: int = 28,
        label_color: tuple[int, int, int] = (200, 200, 200),
        value_color: tuple[int, int, int] = (255, 255, 100)
    ) -> UIText:
        """
        Add a dynamic value display (label + value).
        
        Args:
            key: Key to pass to value provider
            label: Label text to display
            x, y: Position (relative to panel)
            label_size: Font size for label
            value_size: Font size for value
            label_color: Label color
            value_color: Value color
            
        Returns:
            The UIText widget for the value (so caller can update if needed)
        """
        # Create label
        label_text = UIText(
            x,
            y,
            label,
            label_size,
            label_color,
            uid=f"{self.uid}_label_{key}" if self.uid else None
        )
        
        # Create value display (will be updated)
        value_text = UIText(
            x + 200,  # Offset for value
            y,
            "--",  # Placeholder
            value_size,
            value_color,
            text_update=True,
            uid=f"{self.uid}_value_{key}" if self.uid else None
        )
        
        # Set up callback to update from value provider
        def value_callback():
            value = self.get_value(key, "?")
            return str(value)
        
        value_text.set_callback(value_callback)
        
        # Add to panel
        self.add_child(label_text)
        self.add_child(value_text)
        
        # Store reference
        self.value_displays[key] = value_text
        
        return value_text
    
    def add_upgrade_button(
        self,
        key: str,
        name: str,
        cost_key: str,
        x: int,
        y: int,
        w: int,
        h: int,
        on_purchase: Optional[Callable[[str], None]] = None,
        button_color: tuple[int, int, int] = (50, 100, 50),
        text_color: tuple[int, int, int] = (255, 255, 255)
    ) -> UIButton:
        """
        Add an upgrade purchase button.
        
        Args:
            key: Unique identifier for this upgrade
            name: Display name of the upgrade
            cost_key: Key to pass to value provider to get cost
            x, y, w, h: Button position and size
            on_purchase: Callback when button is clicked (receives upgrade key)
            button_color: Button base color
            text_color: Button text color
            
        Returns:
            The UIButton widget
        """
        # Create button
        def on_click():
            if on_purchase:
                on_purchase(key)
        
        button = UIButton(
            x,
            y,
            f"{name}\nCost: ?",
            on_click_callback=on_click,
            w=w,
            h=h,
            color=button_color,
            size_text=24,
            text_color=text_color,
            uid=f"{self.uid}_btn_{key}" if self.uid else None
        )
        
        # Update button text with current cost
        def update_button_text():
            cost = self.get_value(cost_key, "?")
            button.set_text(f"{name}\nCost: {cost}")
        
        # Store update function for refreshing
        button._update_cost = update_button_text
        
        # Initial update
        update_button_text()
        
        # Add to panel
        self.add_child(button)
        
        # Store reference
        self.upgrade_buttons[key] = button
        
        return button
    
    def update_values(self) -> None:
        """Update all value displays and button costs"""
        # Update value displays
        for key, value_text in self.value_displays.items():
            # The text_widget's callback will be called automatically during update
            value_text.update(0)  # Force update
        
        # Update button costs
        for key, button in self.upgrade_buttons.items():
            if hasattr(button, '_update_cost'):
                button._update_cost()
    
    def update(self, dt: float) -> None:
        """Update the upgrade board"""
        super().update(dt)
        # Update dynamic values
        self.update_values()