"""
UICompose - Composite layout widget for arranging children
"""

from typing import TYPE_CHECKING, Optional, List, Tuple, Dict
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font


class UICompose(UIElement):
    """
    Composite widget for laying out children in patterns (grid, horizontal, vertical).
    
    Features:
    - Automatic layout of children in horizontal, vertical, or grid patterns
    - Configurable spacing and alignment
    - Optional wrapping for horizontal/vertical layouts
    """
    
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        layout: str = "horizontal",  # horizontal, vertical, grid
        spacing: int = 10,
        padding: int = 10,
        alignment: str = "start",  # start, center, end, stretch
        uid: Optional[str] = None
    ):
        """
        Initialize UICompose.
        
        Args:
            x, y: Top-left position
            y: Top position
            w, h: Width and height of the container
            layout: Layout type ("horizontal", "vertical", "grid")
            spacing: Space between items in pixels
            padding: Internal padding
            alignment: How to align items ("start", "center", "end", "stretch"). "stretch" gives each child the full cross-axis size and shares the main axis equally
            uid: Unique identifier for layout
        """
        # Store parameters
        self.uid = uid
        self.type = "compose"
        
        # Layout parameters
        self.layout = layout.lower()
        self.spacing = spacing
        self.padding = padding
        self.alignment = alignment.lower()
        
        # Initialize UIElement
        super().__init__(x, y, w, h, uid)
        
        # Track children for layout
        self._children_snapshot: List[UIElement] = []
        # Share of the space each child gets with alignment="stretch" (default 1.0)
        self._weights: Dict[UIElement, float] = {}
    
    def add_child(self, child: UIElement, weight: float = 1.0) -> None:
        """
        Add a child and trigger re-layout.
        
        Args:
            child: UIElement to add
            weight: Share of the space with alignment="stretch" (2.0 gets twice the space of 1.0)
        """
        super().add_child(child)
        self._weights[child] = max(0.0, float(weight))
        self._layout_children()
    
    def remove_child(self, child: UIElement) -> None:
        """
        Remove a child and trigger re-layout.
        
        Args:
            child: UIElement to remove
        """
        super().remove_child(child)
        self._weights.pop(child, None)
        self._layout_children()

    def _shares(self, children: List[UIElement], available: int) -> List[int]:
        """Split `available` pixels (minus spacing) between children according to their weights"""
        room = max(0, available - self.spacing * (len(children) - 1))
        weights = [self._weights.get(c, 1.0) for c in children]
        total = sum(weights)
        if total <= 0:  # all weights are 0: share equally
            weights, total = [1.0] * len(children), float(len(children))
        sizes = [int(room * w / total) for w in weights]
        # Give the rounding leftover to the last child so the row is exactly full
        sizes[-1] += room - sum(sizes)
        return sizes
    
    def _on_layout_applied(self) -> None:
        """Layout loaded after construction: children follow the new size"""
        self._layout_children()

    def _layout_children(self) -> None:
        """Layout all children according to the layout type"""
        if not self.children:
            return
        
        # Get visible children only
        children = [c for c in self.children if c.visible]
        if not children:
            return
        
        # Available space (accounting for padding)
        avail_width = self.rect.width - 2 * self.padding
        avail_height = self.rect.height - 2 * self.padding
        
        if self.layout == "horizontal":
            self._layout_horizontal(children, avail_width, avail_height)
        elif self.layout == "vertical":
            self._layout_vertical(children, avail_width, avail_height)
        elif self.layout == "grid":
            self._layout_grid(children, avail_width, avail_height)
    
    def _layout_horizontal(self, children: List[UIElement], avail_width: int, avail_height: int) -> None:
        """Layout children in a horizontal row"""
        if self.alignment == "stretch":
            # Share the row width equally, every child takes the full available height
            shares = self._shares(children, avail_width)
            for child, share in zip(children, shares):
                child.set_size(share, avail_height)

        # Calculate total width needed
        total_width = sum(c.rect.width for c in children)
        total_width += self.spacing * (len(children) - 1)  # Spacing between items
        
        # Calculate starting x
        start_x = self.padding
        if self.alignment == "center":
            start_x = self.padding + (avail_width - total_width) // 2
        elif self.alignment == "end":
            start_x = self.padding + avail_width - total_width
        # For "start", start_x remains at padding
        
        # Position children
        current_x = start_x
        for child in children:
            # Center vertically
            child_y = self.padding if self.alignment == "stretch" else self.padding + (avail_height - child.rect.height) // 2
            
            # Set position
            child.rect.x = current_x
            child.rect.y = child_y
            
            # Move to next position
            current_x += child.rect.width + self.spacing
    
    def _layout_vertical(self, children: List[UIElement], avail_width: int, avail_height: int) -> None:
        """Layout children in a vertical column"""
        if self.alignment == "stretch":
            # Share the column height equally, every child takes the full available width
            shares = self._shares(children, avail_height)
            for child, share in zip(children, shares):
                child.set_size(avail_width, share)

        # Calculate total height needed
        total_height = sum(c.rect.height for c in children)
        total_height += self.spacing * (len(children) - 1)  # Spacing between items
        
        # Calculate starting y
        start_y = self.padding
        if self.alignment == "center":
            start_y = self.padding + (avail_height - total_height) // 2
        elif self.alignment == "end":
            start_y = self.padding + avail_height - total_height
        # For "start", start_y remains at padding
        
        # Position children
        current_y = start_y
        for child in children:
            # Center horizontally
            child_x = self.padding if self.alignment == "stretch" else self.padding + (avail_width - child.rect.width) // 2
            
            # Set position
            child.rect.x = child_x
            child.rect.y = current_y
            
            # Move to next position
            current_y += child.rect.height + self.spacing
    
    def _layout_grid(self, children: List[UIElement], avail_width: int, avail_height: int) -> None:
        """Layout children in a grid"""
        # For simplicity, we'll make a best-effort grid
        # In a full implementation, we might want to specify columns
        
        # Calculate approximate columns based on average child width
        if children:
            avg_width = sum(c.rect.width for c in children) / len(children)
            cols = max(1, int(avail_width / (avg_width + self.spacing)))
        else:
            cols = 1
        
        # Calculate cell dimensions
        cell_width = (avail_width - self.spacing * (cols - 1)) // cols if cols > 0 else avail_width
        cell_height = avail_height  # Simplified - could calculate based on rows
        
        # Position children
        row = 0
        col = 0
        for child in children:
            x = self.padding + col * (cell_width + self.spacing)
            y = self.padding + row * (child.rect.height + self.spacing)  # Use actual height
            
            # Align within cell
            if self.alignment == "center":
                x += (cell_width - child.rect.width) // 2
            elif self.alignment == "end":
                x += cell_width - child.rect.width
            # For "start", x remains at left edge of cell
            
            child.rect.x = x
            child.rect.y = y
            
            # Move to next position
            col += 1
            if col >= cols:
                col = 0
                row += 1
    
    def update(self, dt: float) -> None:
        """Update - re-layout if children changed"""
        # Check if children list changed
        current_children = [c for c in self.children if c.visible]
        if len(current_children) != len(self._children_snapshot) or \
           any(c1 is not c2 for c1, c2 in zip(current_children, self._children_snapshot)):
            self._layout_children()
            self._children_snapshot = current_children.copy()
        
        super().update(dt)