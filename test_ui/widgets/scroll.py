"""
UIScroll - Scrollable container widget
"""

from typing import TYPE_CHECKING, Optional
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UIScroll(UIElement):
    """
    Vertical scrollable container for UI elements.
    
    Features:
    - Vertical scrolling with mouse wheel or drag
    - Automatic content height calculation
    - Scrollbar visualization
    - Content clipping to viewport
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: tuple[int, int, int] = (30, 30, 35),
        uid: Optional[str] = None
    ):
        """
        Initialize UIScroll.
        
        Args:
            x, y: Top-left position
            w, h: Width and height of the scroll area
            color: Background color RGB tuple
            uid: Unique identifier for layout loading
        """
        # Store parameters
        self.uid = uid
        self.type = "scroll"
        
        # Initialize UIElement
        super().__init__(x, y, w, h, uid)
        
        # Visual properties
        self.color = color
        self.scroll_bar_color = (80, 80, 80)
        self.scroll_bar_active_color = (120, 120, 120)
        self.scroll_bar_width = 10
        
        # State
        self.scroll_offset = 0  # How much we've scrolled vertically
        self.max_scroll = 0     # Maximum scroll value
        self.is_dragging_scrollbar = False
        self.scrollbar_ratio = 0  # Position of scrollbar handle (0-1)
        
        # Create background surface
        self._create_background()
        
        # Content area rect (inside the scroll container)
        self.content_rect = pygame.Rect(
            0,
            0,
            self.rect.width - self.scroll_bar_width,
            self.rect.height
        )
    
    def _create_background(self) -> None:
        """Create the background surface"""
        if hasattr(self, 'panel_factory') and self.panel_factory:
            self.image = self.panel_factory(self.rect.width, self.rect.height, self.color)
        else:
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill(self.color)
    
    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: resize background and content area"""
        self._create_background()
        self.content_rect = pygame.Rect(
            0,
            0,
            self.rect.width - self.scroll_bar_width,
            self.rect.height
        )
        self._update_scroll_limits()

    def add_child(self, child: UIElement) -> None:
        """
        Add a child element and update scroll limits.
        
        Args:
            child: UIElement to add as child
        """
        super().add_child(child)
        self._update_scroll_limits()
    
    def remove_child(self, child: UIElement) -> None:
        """
        Remove a child element and update scroll limits.
        
        Args:
            child: UIElement to remove
        """
        super().remove_child(child)
        self._update_scroll_limits()
    
    def _update_scroll_limits(self) -> None:
        """Calculate maximum scroll based on content height"""
        if not self.children:
            self.max_scroll = 0
            self.scroll_offset = 0
            return
        
        # Find the bottom-most child
        max_bottom = 0
        for child in self.children:
            child_bottom = child.rect.y + child.rect.height
            if child_bottom > max_bottom:
                max_bottom = child_bottom
        
        # Max scroll is how much content sticks out below the viewport
        content_height = max_bottom
        self.max_scroll = max(0, content_height - self.content_rect.height)
        
        # Clamp current scroll offset
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)
        
        # Update scrollbar ratio
        if self.max_scroll > 0:
            self.scrollbar_ratio = self.scroll_offset / self.max_scroll
        else:
            self.scrollbar_ratio = 0
    
    def _get_visible_children(self) -> list:
        """Get list of children that are at least partially visible"""
        visible = []
        view_top = self.scroll_offset
        view_bottom = self.scroll_offset + self.content_rect.height
        
        for child in self.children:
            child_top = child.rect.y
            child_bottom = child.rect.y + child.rect.height
            
            # Check if child overlaps with viewport
            if child_bottom > view_top and child_top < view_bottom:
                visible.append(child)
        
        return visible
    
    def update(self, dt: float) -> None:
        """Update scroll state"""
        super().update(dt)
        
        # Update scrollbar position based on scroll offset
        if self.max_scroll > 0:
            self.scrollbar_ratio = self.scroll_offset / self.max_scroll
        else:
            self.scrollbar_ratio = 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the scroll area and visible children.
        
        Args:
            surface: Target pygame Surface
        """
        if not self.visible:
            return
        
        # Calculate absolute position
        abs_pos = self.get_screen_rect().topleft
        
        # 1. Draw background
        surface.blit(self.image, abs_pos)
        
        # 2. Set up clipping rectangle for content
        clip_rect = pygame.Rect(
            abs_pos[0],
            abs_pos[1],
            self.content_rect.width,
            self.content_rect.height
        )
        
        # Store old clipping rect
        old_clip = surface.get_clip()
        
        # Set clipping to content area
        surface.set_clip(clip_rect)
        
        # 3. Draw visible children (with scroll offset applied)
        for child in self._get_visible_children():
            # Temporarily adjust child's position for scrolling
            original_y = child.rect.y
            child.rect.y -= self.scroll_offset
            
            # Draw child
            child.draw(surface)
            
            # Restore original position
            child.rect.y = original_y
        
        # 4. Restore clipping
        surface.set_clip(old_clip)
        
        # 5. Draw scrollbar (if needed)
        if self.max_scroll > 0:
            self._draw_scrollbar(surface, abs_pos)
    
    def _draw_scrollbar(self, surface: pygame.Surface, abs_pos: tuple[int, int]) -> None:
        """Draw the vertical scrollbar"""
        # Scrollbar background track
        track_x = abs_pos[0] + self.rect.width - self.scroll_bar_width
        track_y = abs_pos[1]
        track_width = self.scroll_bar_width
        track_height = self.rect.height
        
        track_rect = pygame.Rect(track_x, track_y, track_width, track_height)
        track_color = self.scroll_bar_color
        
        # Draw track
        if hasattr(self, 'panel_factory') and self.panel_factory:
            track_surface = self.panel_factory(track_width, track_height, track_color)
        else:
            track_surface = pygame.Surface((track_width, track_height))
            track_surface.fill(track_color)
        
        surface.blit(track_surface, (track_x, track_y))
        
        # Scrollbar handle
        if self.max_scroll > 0:
            handle_height = max(20, int(track_height * (self.rect.height / (self.rect.height + self.max_scroll))))
            handle_y = track_y + int((track_height - handle_height) * self.scrollbar_ratio)
            
            handle_rect = pygame.Rect(track_x, handle_y, track_width, handle_height)
            handle_color = self.scroll_bar_active_color if self.is_dragging_scrollbar else self.scroll_bar_color
            
            # Make handle slightly lighter when not dragging for visual feedback
            if not self.is_dragging_scrollbar:
                # Already using base color, could make it slightly darker when dragging
                pass
            
            if hasattr(self, 'panel_factory') and self.panel_factory:
                handle_surface = self.panel_factory(track_width, handle_height, handle_color)
            else:
                handle_surface = pygame.Surface((track_width, handle_height))
                handle_surface.fill(handle_color)
            
            surface.blit(handle_surface, (track_x, handle_y))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for scrolling.
        
        Args:
            event: pygame Event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over scrollbar
        scrollbar_x = abs_rect.right - self.scroll_bar_width
        scrollbar_rect = pygame.Rect(
            scrollbar_x,
            abs_rect.top,
            self.scroll_bar_width,
            abs_rect.height
        )
        is_over_scrollbar = scrollbar_rect.collidepoint(mouse_pos)
        
        # Mouse wheel scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                if abs_rect.collidepoint(mouse_pos):
                    self._scroll(-20)  # Scroll up by 20 pixels
                    return True
            elif event.button == 5:  # Scroll down
                if abs_rect.collidepoint(mouse_pos):
                    self._scroll(20)   # Scroll down by 20 pixels
                    return True
        
        # Scrollbar dragging
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_over_scrollbar and self.max_scroll > 0:
                self.is_dragging_scrollbar = True
                # Calculate offset within scrollbar
                rel_y = mouse_pos[1] - scrollbar_rect.top
                track_height = abs_rect.height
                handle_height = max(20, int(track_height * (self.rect.height / (self.rect.height + self.max_scroll))))
                self.scrollbar_drag_offset = rel_y - (handle_height // 2)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging_scrollbar:
                self.is_dragging_scrollbar = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
            if self.max_scroll > 0:
                # Calculate new scrollbar position
                rel_y = mouse_pos[1] - abs_rect.top - self.scrollbar_drag_offset
                track_height = abs_rect.height
                handle_height = max(20, int(track_height * (self.rect.height / (self.rect.height + self.max_scroll))))
                
                # Constrain to track bounds
                max_y = track_height - handle_height
                rel_y = max(0, min(rel_y, max_y))
                
                # Convert to scroll ratio
                if max_y > 0:
                    self.scrollbar_ratio = rel_y / max_y
                    self.scroll_offset = int(self.scrollbar_ratio * self.max_scroll)
                return True
        
        # Let children handle event (but adjust coordinates for scrolling)
        elif self.children and abs_rect.collidepoint(mouse_pos):
            # Create a copy of event with adjusted coordinates for children
            # For simplicity, we'll let children get the event and handle scrolling in their hit detection
            # A more sophisticated approach would adjust event coordinates
            pass
        
        return False
    
    def _scroll(self, delta_y: int) -> None:
        """
        Scroll by a delta amount.
        
        Args:
            delta_y: Pixels to scroll (positive = down, negative = up)
        """
        if self.max_scroll > 0:
            self.scroll_offset = max(0, min(self.scroll_offset + delta_y, self.max_scroll))
            self._update_scroll_limits()  # This will update scrollbar_ratio