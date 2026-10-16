"""
UIElement - Base class for all UI elements
Scene graph, layout, rendering, animation, edit mode
"""

from typing import TYPE_CHECKING, Optional, Callable, Dict, Any, List
import pygame

if TYPE_CHECKING:
    import pygame.font


class UIElement:
    """
    Base UI element with scene graph capabilities.
    
    Features:
    - Scene graph (parent/children)
    - Absolute position calculation
    - Recursive draw/update
    - Layout injection (optional JSON config)
    - Event bus injection (optional)
    - Panel factory injection (optional, class-level or per-instance)
    - Animation (target/lerp)
    - Edit mode visual (pink outline)
    - Auto-configuration from layout cache
    
    Styling / Theming:
    -------------------
    Tous les widgets qui ont besoin d'une surface de fond (UIButton, UIPanel,
    UISlider, UISwitch, UIScroll, UIProgressBar, etc.) utilisent
    ``self.panel_factory(w, h, color)`` pour generer leur image.
    
    Tu peux brancher ton propre renderer de 2 facons :
    
    1. **Global (classe)** — tous les widgets heritent du meme style :
    
        UIElement.set_default_panel_factory(my_panel_factory)

    2. **Local (instance)** — un widget particulier a son propre style :
    
        bouton.set_panel_factory(mon_renderer_perso)
    
    Le resolution order : instance override > class default > fallback (solide).
    """

    # Class-level panel factory (default for all instances)
    _default_panel_factory: Optional[Callable] = None

    # Class-level layout cache ({uid: {x, y, w, h}}), applied to every element
    _default_layout_cache: Dict[str, dict] = {}

    @classmethod
    def set_default_layout_cache(cls, layout: Optional[Dict[str, dict]]) -> None:
        """
        Set the layout used by every element (at construction and when added to a tree).

        Passing None or {} clears it.
        """
        UIElement._default_layout_cache = layout if layout is not None else {}

    @classmethod
    def set_default_panel_factory(cls, factory: Optional[Callable]) -> None:
        """
        Definit la panel factory par defaut pour TOUS les widgets.
        
        ``factory(w, h, color) -> pygame.Surface``
        
        Exemple:
            UIElement.set_default_panel_factory(my_panel_factory)
        """
        cls._default_panel_factory = factory
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        w: int, 
        h: int, 
        uid: Optional[str] = None
    ):
        """
        Initialize UI element.
        
        Args:
            x, y: Top-left position
            w, h: Width and height
            uid: Unique identifier for layout loading
        """
        self.uid = uid
        self.scroll_offset = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, w, h)
        self.cfg_loaded = False
        
        # Pre-init injected deps
        self._event_bus = None
        self._panel_factory = None
        
        # Auto-configuration from the layout cache (overrides x,y,w,h)
        entry = self._layout_entry()
        if entry is not None:
            self._apply_layout_entry(entry)

        self.absolute_rect = None
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.start_pos = self.pos.copy()

        # Visual surface (transparent by default)
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)

        # State
        self.debug = False
        self.visible: bool = True
        self.active: bool = True
        self.type: str = "element"
        self.parent: Optional["UIElement"] = None
        self.children: List["UIElement"] = []

        # Animation
        self.target: Optional[tuple] = None
        self.speed: int = 300  # pixels per second
        self.bouncing: bool = False
        self.start_pos = (x, y)
        self.end_pos = None

    # ==========================
    # Dependency Injection
    # ==========================

    def set_layout_cache(self, layout_cache: Dict[str, dict]) -> None:
        """
        Inject the layout (from JSON) and apply it to this element and its whole subtree.
        
        The layout is shared by all elements, so elements created later also use it.
        """
        UIElement.set_default_layout_cache(layout_cache)
        self.apply_layout()

    def _layout_entry(self) -> Optional[dict]:
        """Return this element's saved layout entry, or None if it has none"""
        if not self.uid:
            return None
        entry = UIElement._default_layout_cache.get(self.uid)
        return entry if isinstance(entry, dict) else None

    def _apply_layout_entry(self, cfg: dict) -> bool:
        """
        Apply one {x, y, w, h} entry to the rect. Missing keys keep the current value.
        
        Returns False (and leaves the rect untouched) if the entry holds non-integer values.
        """
        try:
            x = int(cfg.get("x", self.rect.x))
            y = int(cfg.get("y", self.rect.y))
            w = int(cfg.get("w", self.rect.width))
            h = int(cfg.get("h", self.rect.height))
        except (TypeError, ValueError):
            print(f"Invalid layout entry for '{self.uid}': {cfg}")
            return False
        self.rect.update(x, y, max(0, w), max(0, h))
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.cfg_loaded = True
        return True

    def apply_layout(self) -> None:
        """
        Apply the current layout cache to this element and all its descendants.
        
        Calls ``_on_layout_applied`` on each element whose entry was applied, so
        widgets can rebuild surfaces that depend on their size.
        """
        entry = self._layout_entry()
        if entry is not None and self._apply_layout_entry(entry):
            self._on_layout_applied()
        for child in self.children:
            child.apply_layout()

    def set_size(self, w: int, h: int) -> None:
        """Resize the element and rebuild the surfaces that depend on its size"""
        self.rect.size = (max(0, w), max(0, h))
        self._on_layout_applied()

    def _on_layout_applied(self) -> None:
        """Hook: called after a layout entry is applied to this element (override in widgets)"""
        pass

    def set_event_bus(self, event_bus: Any):
        """Inject event bus for publishing/subscribing"""
        self._event_bus = event_bus

    def set_panel_factory(self, panel_factory: Callable):
        """Inject factory function for creating UI panel surfaces"""
        self._panel_factory = panel_factory

    # ==========================
    # Scene Graph Management
    # ==========================

    def home_position(self) -> None:
        """Update initial position if element is a child"""
        self.absolute_rect = self.get_screen_rect()

    def add_child(self, new_child: "UIElement") -> None:
        """Add a child element"""
        self.children.append(new_child)
        new_child.parent = self
        new_child.home_position()
        # Elements built before the layout was loaded pick it up here
        new_child.apply_layout()

    def remove_child(self, child: "UIElement") -> None:
        """Remove a specific child"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def remove_all_children(self) -> None:
        """Remove all children"""
        for child in self.children[:]:
            self.remove_child(child)

    # ==========================
    # Geometry & Rendering
    # ==========================

    def get_screen_rect(self) -> pygame.Rect:
        """Get absolute screen position"""
        abs_x = self.rect.x
        abs_y = self.rect.y
        
        current = self.parent
        while current is not None:
            abs_x += current.rect.x - current.scroll_offset.x
            abs_y += current.rect.y - current.scroll_offset.y
            current = current.parent
            
        return pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)

    def get_size(self) -> pygame.Rect:
        """Get bounding rect including all children"""
        total_rect = self.get_screen_rect()
        
        for child in self.children:
            total_rect.union_ip(child.get_size())
            
        return total_rect

    # ==========================
    # Game Loop Integration
    # ==========================

    def update(self, dt: float) -> None:
        """Update element and children (animation, etc.)"""
        if not self.visible:
            return

        # Animation: move toward target
        if self.target:
            tx, ty = self.target
            vec = pygame.math.Vector2(tx - self.rect.x, ty - self.rect.y)
            dist = vec.length()

            if dist > self.speed / 100:  # Not close enough
                vec.normalize_ip()
                self.rect.x += vec.x * self.speed * dt
                self.rect.y += vec.y * self.speed * dt
            else:  # Arrived
                self.rect.x = tx
                self.rect.y = ty
                self.target = None

        # Update children
        for child in self.children:
            child.update(dt)

    def handle_event(self, event) -> bool:
        """
        Handle pygame event. Returns True if event was handled.
        
        Order: children (top-to-bottom) -> self
        """
        if not self.visible:
            return False

        # Let children handle event first (back-to-front rendering order)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True

        return False  # Not handled by anyone

    def set_child(self, argument: str, own: bool = True) -> None:
        """
        Toggle a boolean attribute on self and optionally children.
        Used for debug mode toggling.
        """
        if hasattr(self, argument):
            attr_value = getattr(self, argument)
            if isinstance(attr_value, bool):
                if own:
                    setattr(self, argument, not attr_value)
                # Propagate to children
                if self.children:
                    for child in self.children:
                        child.set_child(argument)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw element and children to surface.
        
        Args:
            surface: Target pygame Surface
        """
        if not self.visible:
            return

        # Draw self
        abs_rect = self.get_screen_rect()
        surface.blit(self.image, abs_rect)
        
        # Edit mode outline (pink)
        if self.debug:
            pygame.draw.rect(surface, (255, 0, 255), abs_rect, 2)

        # Draw children
        for child in self.children:
            child.draw(surface)

    # ==========================
    # Animation
    # ==========================

    def reset_position(self) -> None:
        """Reset to initial position"""
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.target = None

    def show(self) -> None:
        """Show element (reset position if has start/end)"""
        self.visible = True
        if self.start_pos and self.end_pos:
            self.target = self.start_pos

    def hide(self) -> None:
        """Hide element"""
        self.visible = False

    def kill(self) -> None:
        """Hide and optionally animate to end position"""
        if not self.end_pos:
            self.visible = False
        else:
            self.target = self.end_pos

    def set_animation(
        self,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        speed: int = 300,
        bouncing: bool = False,
    ) -> None:
        """Set up animation between two points"""
        self.bouncing = bouncing
        self.speed = speed
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.target = start_pos  # Start at beginning

    # ==========================
    # Helper Properties
    # ==========================

    @property
    def layout_cache(self) -> Optional[Dict]:
        """Get the layout cache shared by all elements"""
        return UIElement._default_layout_cache

    @property
    def event_bus(self) -> Optional[Any]:
        """Get injected event bus"""
        return self._event_bus

    @property
    def panel_factory(self) -> Optional[Callable]:
        """
        Get the effective panel factory for this element.
        
        Resolution order:
        1. Instance override (via set_panel_factory)
        2. Class default (via UIElement.set_default_panel_factory)
        3. None (fallback → couleurs solides pygame)
        """
        if self._panel_factory is not None:
            return self._panel_factory
        # Use __class__ to avoid bound-method transformation
        return type(self)._default_panel_factory


# Export for backward compatibility
__all__ = ["UIElement"]