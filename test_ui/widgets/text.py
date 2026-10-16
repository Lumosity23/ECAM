"""
UIText - Text label widget
"""

from typing import TYPE_CHECKING, Optional, Callable, Union
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIText(UIElement):
    """
    Text label widget with optional auto-updating content.
    
    Features:
    - Font injection via UIText.set_font_provider(dict[int, pygame.font.Font])
    - Text alignment options
    - Optional callback for dynamic text updates
    - Font caching for performance
    """
    
    # Class-level font cache (injected via set_font_provider)
    _FONTS_CACHE: dict[int, pygame.font.Font] = {}
    
    @classmethod
    def set_font_provider(cls, fonts_dict: dict[int, pygame.font.Font]) -> None:
        """
        Inject font dictionary for text rendering.
        
        Args:
            fonts_dict: Dictionary mapping font sizes to pygame.font.Font objects
        """
        cls._FONTS_CACHE = fonts_dict
    
    def __init__(
        self,
        x: int,
        y: int,
        text_or_callback: Union[str, Callable[[], str]],
        size_text: int = 50,
        color: tuple[int, int, int] = (255, 255, 255),
        align: str = 'topleft',
        text_update: bool = False,
        uid: Optional[str] = None
    ):
        """
        Initialize UIText.
        
        Args:
            x, y: Position (interpreted based on align parameter)
            text_or_callback: Static text string OR callable that returns string
            size_text: Font size in pixels
            color: RGB color tuple
            align: Alignment - 'topleft', 'topright', 'bottomleft', 'bottomright',
                   'midtop', 'midleft', 'midbottom', 'midright', 'center'
            text_update: If True, treat text_or_callback as a callable for dynamic updates
            uid: Unique identifier for layout loading
        """
        # Store parameters before calling super().__init__
        self.uid = uid
        self.type = "text"
        self.text_update = text_update
        self.color = color
        self.align = align
        self.size_text = size_text
        
        # Store either static text or callback
        if text_update and callable(text_or_callback):
            self.text_callback: Callable[[], str] = text_or_callback
            self.static_text: str = ""
        else:
            self.text_callback = None
            self.static_text = str(text_or_callback)
            
        # Initialize cache before _render_text (dynamic text check)
        self._cache: dict[str, pygame.Surface] = {}

        # Initialize UIElement base with zero size (will be set after text render)
        super().__init__(x, y, 0, 0, uid)
        
        # Create initial surface and set proper size
        self._render_text()
        
        # Set rect based on alignment (if not loaded from layout)
        if not self.cfg_loaded:
            temp_rect = self.image.get_rect()
            setattr(temp_rect, self.align, (x, y))
            self.rect.x = temp_rect.x
            self.rect.y = temp_rect.y

    def _get_font(self, size: int) -> pygame.font.Font:
        """Get font from cache, falling back to closest size"""
        font = self._FONTS_CACHE.get(size)
        if font is None and self._FONTS_CACHE:
            # Find closest available size
            closest_size = min(self._FONTS_CACHE.keys(), 
                             key=lambda s: abs(s - size))
            return self._FONTS_CACHE[closest_size]
        # Fallback to default font if nothing available
        return pygame.font.Font(None, size)
    
    def _render_text(self) -> None:
        """Render the text surface"""
        # Get current text (static or from callback)
        if self.text_update and self.text_callback:
            text = str(self.text_callback())
        else:
            text = self.static_text
            
        # Get font
        font = self._get_font(self.size_text)
        
        # Check cache for dynamic text
        if self.text_update and text in self._cache:
            self.image = self._cache[text].copy()
        else:
            # Render new surface
            self.image = font.render(text, True, self.color)
            # Cache if dynamic (limit cache size)
            if self.text_update:
                self._cache[text] = self.image.copy()
                if len(self._cache) > 100:  # Limit cache size
                    # Remove oldest entry (simple FIFO)
                    for key in list(self._cache.keys())[:-50]:
                        del self._cache[key]
        # The rect has the size of the text, so containers can center it
        self.rect.size = self.image.get_size()
    
    def set_text(self, text: str, size: Optional[int] = None, 
                 color: Optional[tuple[int, int, int]] = None) -> None:
        """
        Update the text properties.
        
        Args:
            text: New text string
            size: New font size (optional)
            color: New color (optional)
        """
        if not self.text_update:  # Only for static text
            self.static_text = str(text)
            if size is not None:
                self.size_text = size
            if color is not None:
                self.color = color
            self._render_text()
            # Update rect to maintain position
            old_topleft = self.rect.topleft
            self.rect = self.image.get_rect(**{self.align: self.rect.topleft})
            self.rect.topleft = old_topleft
    
    def set_color(self, color: tuple[int, int, int]) -> None:
        """Update text color"""
        self.color = color
        self._render_text()
    
    def set_font_size(self, size: int) -> None:
        """Update font size"""
        self.size_text = size
        self._render_text()
    
    def set_callback(self, callback: Callable[[], str]) -> None:
        """Set/update the text callback for dynamic updates"""
        self.text_callback = callback
        self.text_update = True
        self._render_text()
    
    def update(self, dt: float) -> None:
        """Update - re-render if using dynamic text"""
        super().update(dt)
        
        if self.text_update:
            # Re-render and update if changed
            old_image = self.image
            self._render_text()
            if self.image is not old_image:
                # Surface changed, need to update rect position
                old_topleft = self.rect.topleft
                self.rect = self.image.get_rect(**{self.align: self.rect.topleft})
                self.rect.topleft = old_topleft