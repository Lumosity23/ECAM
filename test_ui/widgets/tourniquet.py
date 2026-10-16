"""
UITourniquet - Horizontal carousel/widget selector
"""

from typing import TYPE_CHECKING, Optional, List, Callable
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font


class UITourniquet(UIElement):
    """
    Horizontal carousel for selecting from a list of items.
    
    Features:
    - Horizontal scrolling of items
    - Center item highlighted/focused
    - Mouse click and drag to scroll
    - Mouse wheel support
    - Optional title display
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        items: List[str],
        uid: Optional[str] = None
    ):
        """
        Initialize UITourniquet.
        
        Args:
            x, y: Center position of the tornequet
            w, h: Width and height of the tornequet display area
            items: List of strings to display
            uid: Unique identifier for loading layout
        """
        # Store parameters
        self.uid = uid
        self.type = "tourniquet"
        
        # Initialize UIElement (note: x,y passed as center, so we adjust)
        super().__init__(x - w//2, y - h//2, w, h, uid)
        
        # Store center position for reference
        self.center_x = x
        self.center_y = y
        
        # Data
        self.items = items[:]
        self.item_surfaces: List[pygame.Surface] = []
        self.item_rects: List[pygame.Rect] = []
        
        # State
        self.selected_index = 0
        self.offset_x = 0  # Horizontal offset for scrolling
        self.target_offset_x = 0
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_offset = 0
        
        # Appearance
        self.item_spacing = 20
        self.item_scale_factor = 0.8  # Non-selected items scale
        self.selected_scale = 1.0
        self.item_height_ratio = 0.8  # Item height relative to tourniquet height
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.item_bg_color = (50, 50, 60)
        self.item_bg_selected_color = (80, 80, 100)
        self.text_color = (200, 200, 200)
        self.text_color_selected = (255, 255, 255)
        
        # Font
        self.font_size = int(h * 0.4)
        
        # Create title label (optional)
        self.title_label: Optional[UIText] = None
        
        # Render items
        self._render_items()
    
    def set_title(self, text: str, size: int = 24) -> None:
        """
        Set a title for the tornequet.
        
        Args:
            text: Title text
            size: Font size for title
        """
        from pygame_ui.widgets.text import UIText
        
        if self.title_label:
            self.remove_child(self.title_label)
        
        self.title_label = UIText(
            self.rect.centerx,
            self.rect.top - 30,
            text,
            size,
            uid=f"{self.uid}_title" if self.uid else None
        )
        self.add_child(self.title_label)
    
    def _render_items(self) -> None:
        """Render all item surfaces"""
        self.item_surfaces = []
        self.item_rects = []
        
        if not self.items:
            return
        
        # Font for items
        font_size = int(self.rect.height * self.item_height_ratio)
        font = pygame.font.Font(None, font_size)
        
        # Create surface for each item
        for i, item in enumerate(self.items):
            # Create text surface
            is_selected = (i == self.selected_index)
            color = self.text_color_selected if is_selected else self.text_color
            text_surface = font.render(item, True, color)
            
            # Create background surface with padding
            padding = 20
            surf_width = text_surface.get_width() + 2 * padding
            surf_height = text_surface.get_height() + 10
            
            # Choose background color
            bg_color = self.item_bg_selected_color if is_selected else self.item_bg_color
            
            # Create surface
            surface = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
            
            # Draw rounded rectangle background
            rect = surface.get_rect()
            corner_radius = min(surf_height // 2, 10)
            pygame.draw.rect(surface, bg_color, rect, border_radius=corner_radius)
            
            # Blit text onto surface
            text_x = (surf_width - text_surface.get_width()) // 2
            text_y = (surf_height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
            self.item_surfaces.append(surface)
            
            # Create rect for positioning
            item_rect = surface.get_rect()
            self.item_rects.append(item_rect)
    
    def _layout_items(self) -> None:
        """Position items horizontally based on offset"""
        if not self.items:
            return
        
        # Start position (centered)
        total_width = 0
        for surf in self.item_surfaces:
            total_width += surf.get_width() + self.item_spacing
        
        # Start x position so that the sequence is centered
        start_x = (self.rect.width - total_width + self.item_spacing) // 2 + self.offset_x
        
        current_x = start_x
        for i, surface in enumerate(self.item_surfaces):
            # Calculate scale based on distance from center
            item_center_x = current_x + surface.get_width() // 2
            distance_from_center = abs(item_center_x - self.rect.centerx)
            
            # Calculate scale: closer to center = larger
            max_distance = self.rect.width // 2
            distance_factor = min(1.0, distance_from_center / max_distance)
            
            # Interpolate scale between min and max
            scale = self.item_scale_factor + (self.selected_scale - self.item_scale_factor) * (1.0 - distance_factor)
            
            # Apply scale
            scaled_width = int(surface.get_width() * scale)
            scaled_height = int(surface.get_height() * scale)
            scaled_surface = pygame.transform.smoothscale(surface, (scaled_width, scaled_height))
            
            # Position
            y_pos = (self.rect.height - scaled_height) // 2
            rect = pygame.Rect(current_x, y_pos, scaled_width, scaled_height)
            
            # Store for rendering/hit testing
            if not hasattr(self, '_scaled_surfaces'):
                self._scaled_surfaces = []
                self._scaled_rects = []
            
            # Ensure lists are long enough
            while len(self._scaled_surfaces) <= i:
                self._scaled_surfaces.append(None)
                self._scaled_rects.append(None)
                
            self._scaled_surfaces[i] = scaled_surface
            self._scaled_rects[i] = rect
            
            # Move to next item position
            current_x += surface.get_width() + self.item_spacing
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the tornequet.
        
        Args:
            surface: Target pygame Surface
        """
        if not self.visible:
            return
        
        # Update scaled surfaces and positions
        self._layout_items()
        
        # Draw background
        abs_pos = self.get_screen_rect().topleft
        if hasattr(self, 'panel_factory') and self.panel_factory:
            bg_surface = self.panel_factory(self.rect.width, self.rect.height, self.bg_color)
        else:
            bg_surface = pygame.Surface((self.rect.width, self.rect.height))
            bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, abs_pos)
        
        # Draw items
        if hasattr(self, '_scaled_surfaces'):
            for i, (surf, rect) in enumerate(zip(self._scaled_surfaces, self._scaled_rects)):
                if surf is not None:
                    # Calculate absolute position
                    abs_x = abs_pos[0] + rect.x
                    abs_y = abs_pos[1] + rect.y
                    surface.blit(surf, (abs_x, abs_y))
        
        # Draw children (title, etc.)
        super().draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the tornequet.
        
        Args:
            event: pygame Event to process
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # Mouse wheel scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up/left
                if abs_rect.collidepoint(mouse_pos):
                    self._select_previous()
                    return True
            elif event.button == 5:  # Scroll down/right
                if abs_rect.collidepoint(mouse_pos):
                    self._select_next()
                    return True
        
        # Mouse drag to scroll
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self.drag_start_x = mouse_pos[0]
                self.drag_start_offset = self.offset_x
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                # Snap to nearest item
                self._snap_to_item()
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx = mouse_pos[0] - self.drag_start_x
            self.offset_x = self.drag_start_offset + dx
            self._layout_items()  # Update positions immediately during drag
            return True
        
        # Let children handle event
        return super().handle_event(event)
    
    def _select_next(self) -> None:
        """Select the next item in the list"""
        if not self.items:
            return
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self._update_offset_for_selected()
        self._render_items()
    
    def _select_previous(self) -> None:
        """Select the previous item in the list"""
        if not self.items:
            return
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self._update_offset_for_selected()
        self._render_items()
    
    def _update_offset_for_selected(self) -> None:
        """Adjust offset so selected item is centered"""
        if not self.items or not self.item_surfaces:
            return
        
        # Get width of selected item
        selected_surface = self.item_surfaces[self.selected_index]
        selected_width = selected_surface.get_width()
        
        # Calculate offset to center this item
        target_offset = (self.rect.width // 2) - selected_width // 2
        
        # Subtract the position of the item in the unoffset layout
        # We need to calculate where this item would be at offset=0
        items_before_width = 0
        for i in range(self.selected_index):
            if i < len(self.item_surfaces):
                items_before_width += self.item_surfaces[i].get_width() + self.item_spacing
        
        self.target_offset_x = target_offset - items_before_width
    
    def _snap_to_item(self) -> None:
        """Snap to the nearest item based on current offset"""
        if not self.items:
            return
        
        # Find which item is closest to center
        best_distance = float('inf')
        best_index = self.selected_index
        
        # Calculate position of each item at current offset
        current_x = (self.rect.width - sum(s.get_width() + self.item_spacing for s in self.item_surfaces) + self.item_spacing) // 2 + self.offset_x
        
        for i, surface in enumerate(self.item_surfaces):
            item_center_x = current_x + surface.get_width() // 2
            distance = abs(item_center_x - self.rect.centerx)
            
            if distance < best_distance:
                best_distance = distance
                best_index = i
            
            current_x += surface.get_width() + self.item_spacing
        
        # Update selection if changed
        if best_index != self.selected_index:
            self.selected_index = best_index
            self._render_items()
        
        # Smoothly animate to centered position
        self._update_offset_for_selected()
    
    def update(self, dt: float) -> None:
        """Update animation"""
        super().update(dt)
        
        # Smoothly animate offset toward target
        if hasattr(self, 'target_offset_x'):
            diff = self.target_offset_x - self.offset_x
            if abs(diff) > 0.5:
                self.offset_x += diff * 0.1  # Smooth damping
                self._layout_items()
            else:
                self.offset_x = self.target_offset_x
    
    def get_selected(self) -> Optional[str]:
        """Get the currently selected item"""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def get_selected_index(self) -> int:
        """Get the index of the currently selected item"""
        return self.selected_index
    
    def set_items(self, items: List[str]) -> None:
        """Update the list of items"""
        self.items = items[:]
        self.selected_index = min(self.selected_index, len(self.items) - 1) if self.items else 0
        self._render_items()
        self._update_offset_for_selected()