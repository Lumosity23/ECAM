"""
UIManager - Root UI container and event handler
"""

from typing import TYPE_CHECKING, Optional, Callable, Dict, Any
import json
import os
import pygame

from pygame_ui.core.ui_element import UIElement

if TYPE_CHECKING:
    import pygame.font

# File used by save_layout_to_file() when no path has been set (created in the working dir)
DEFAULT_LAYOUT_FILE = "layout.json"


def _clean_layout(layout: Any) -> Dict[str, dict]:
    """Keep only {uid: {x, y, w, h}} entries that are dicts; report the others"""
    if not isinstance(layout, dict):
        print("Layout must be a JSON object, ignoring it")
        return {}
    clean: Dict[str, dict] = {}
    for uid, cfg in layout.items():
        if isinstance(cfg, dict):
            clean[uid] = cfg
        else:
            print(f"Layout entry '{uid}' is not an object, ignoring it")
    return clean


def _read_layout_file(filepath: str) -> Dict[str, dict]:
    """Read a layout file. Missing or broken files give an empty layout."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading layout from {filepath} ({e}), using empty layout")
        return {}
    return _clean_layout(data)


class UIManager:
    """
    Manages the UI hierarchy and input/events.
    
    Responsibilities:
    - Holds root UIElement (full screen)
    - Manages named UI panels (menus, settings, HUD, etc.)
    - Handles pygame events (including edit mode with F1)
    - Routes events to UI hierarchy
    - Optional dependency injection:
        - Event bus (for gameplay events like MENU, PAUSE, etc.)
        - Panel factory (for creating panel surfaces)
        - Layout loader/saver (for JSON persistence)
        - Value providers (for dynamic widgets)
    - Edit mode: F1 toggles pink outlines, drag to move, Ctrl+S save layout
    """
    
    def __init__(
        self,
        screen_size: tuple[int, int],
        enable_edit_mode: bool = False,
    ):
        """
        Initialize UIManager.
        
        Args:
            screen_size: (width, height) of the display
            enable_edit_mode: Start with edit mode enabled (default: False)
        """
        pygame.font.init()
        self.screen_size = screen_size
        self.edit_mode = enable_edit_mode
        
        # Layout management
        self.layout: Dict = {}
        self.layout_path: Optional[str] = None
        self._layout_saver: Optional[Callable[[Dict], None]] = None
        
        # Injected dependencies (set via injector methods)
        self._event_bus: Optional[Any] = None
        self._panel_factory: Optional[Callable] = None
        self._save_manager: Optional[Any] = None
        self._sprite_manager: Optional[Any] = None
        self._value_provider: Optional[Callable] = None
        self._font_provider: Optional[Dict[int, pygame.font.Font]] = None
        
        # Root element (full screen)
        self.root = UIElement(
            0, 0, screen_size[0], screen_size[1], uid="ROOT"
        )
        
        # Edit mode state
        self.selected_element: Optional[UIElement] = None
        self.offset_x = 0
        self.offset_y = 0
        
        # UI panels (will be set via setter methods or direct assignment)
        self.panels: Dict[str, UIElement] = {}

    # ==========================
    # Dependency Injection
    # ==========================

    def inject(
        self,
        event_bus: Optional[Any] = None,
        panel_factory: Optional[Callable] = None,
        save_manager: Optional[Any] = None,
        sprite_manager: Optional[Any] = None,
        value_provider: Optional[Callable] = None,
        font_provider: Optional[Dict[int, pygame.font.Font]] = None,
        layout_loader: Optional[Callable[[], Dict]] = None,
        layout_saver: Optional[Callable[[Dict], None]] = None,
    ) -> None:
        """Inject dependencies"""
        if event_bus is not None:
            self._event_bus = event_bus
        if panel_factory is not None:
            self._panel_factory = panel_factory
            UIElement.set_default_panel_factory(panel_factory)
        if save_manager is not None:
            self._save_manager = save_manager
        if sprite_manager is not None:
            self._sprite_manager = sprite_manager
        if value_provider is not None:
            self._value_provider = value_provider
        if font_provider is not None:
            self._font_provider = font_provider
            # Propagate to UIText
            from pygame_ui.widgets.text import UIText
            UIText.set_font_provider(font_provider)
        if layout_loader is not None:
            self.layout = layout_loader()
            self.root.set_layout_cache(self.layout)
        if layout_saver is not None:
            self._layout_saver = layout_saver

    # Convenience setters
    def set_event_bus(self, event_bus: Any) -> None:
        self._event_bus = event_bus
        
    def set_panel_factory(self, panel_factory: Callable) -> None:
        """Set panel factory globally (class-level default)"""
        self._panel_factory = panel_factory
        UIElement.set_default_panel_factory(panel_factory)
        
    def set_save_manager(self, save_manager: Any) -> None:
        self._save_manager = save_manager
        
    def set_sprite_manager(self, sprite_manager: Any) -> None:
        self._sprite_manager = sprite_manager
        
    def set_value_provider(self, value_provider: Callable) -> None:
        self._value_provider = value_provider
        
    def set_font_provider(self, font_provider: Dict[int, pygame.font.Font]) -> None:
        self._font_provider = font_provider
        from pygame_ui.widgets.text import UIText
        UIText.set_font_provider(font_provider)
        
    def set_layout(self, layout: Dict) -> None:
        """Set layout directly and apply it to every element in the tree"""
        self.layout = _clean_layout(layout)
        self.root.set_layout_cache(self.layout)

    def load_layout_from_file(self, filepath: str) -> None:
        """Load a layout JSON file and apply it to the UI tree. Remembers the path for saving."""
        self.layout_path = filepath
        self.set_layout(_read_layout_file(filepath))

    def save_layout_to_file(self, filepath: Optional[str] = None) -> str:
        """
        Save the positions and sizes of every uid in the UI tree.

        - With ``filepath``, saves there and remembers it for next time.
        - Without a path, uses the remembered one, or creates ``layout.json`` in the
          working directory if none was ever set.
        - Entries already in the file for uids not in the tree are kept.

        Returns the path the layout was saved to.
        """
        if filepath is not None:
            self.layout_path = filepath
        if self.layout_path is None:
            self.layout_path = os.path.abspath(DEFAULT_LAYOUT_FILE)
            print(f"No layout file set, using {self.layout_path}")
        path = self.layout_path

        # Merge with what is already on disk so unrelated entries survive
        existing = _read_layout_file(path) if os.path.exists(path) else {}
        data = {**existing, **self._collect_layout()}

        if not self._collect_layout():
            print("Warning: no element with a uid is in the UI tree, nothing new to save")

        try:
            # Write to a temp file first so a crash never leaves a half-written layout
            tmp_path = f"{path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            os.replace(tmp_path, path)
        except OSError as e:
            print(f"Error saving layout to {path}: {e}")
            return path

        # Optional extra hook (e.g. to also store the layout somewhere else)
        if self._layout_saver is not None:
            self._layout_saver(data)

        UIElement.set_default_layout_cache(data)
        self.layout = data
        print(f"Layout saved to {path}")
        return path

    def _collect_layout(self) -> Dict[str, dict]:
        """Collect {uid: {x, y, w, h}} for every element in the tree (root excluded)"""
        data: Dict[str, dict] = {}

        def collect(element: UIElement) -> None:
            if element.uid and element is not self.root:
                data[element.uid] = {
                    "x": element.rect.x,
                    "y": element.rect.y,
                    "w": element.rect.width,
                    "h": element.rect.height,
                }
            for child in element.children:
                collect(child)

        collect(self.root)
        return data

    # ==========================
    # Panel Management
    # ==========================

    def register_panel(self, name: str, panel: UIElement) -> None:
        """Register a panel for easy access"""
        self.panels[name] = panel
        self.root.add_child(panel)
        
    def get_panel(self, name: str) -> Optional[UIElement]:
        """Get a registered panel by name"""
        return self.panels.get(name)
        
    def show_panel(self, name: str) -> None:
        """Show a specific panel, hide others"""
        for panel_name, panel in self.panels.items():
            panel.visible = (panel_name == name)
            
    def hide_all_panels(self) -> None:
        """Hide all registered panels"""
        for panel in self.panels.values():
            panel.visible = False

    # ==========================
    # Event Handling
    # ==========================

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Main event entry point.
        Returns True if event was consumed by UI.
        """
        # F1 toggles edit mode
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.toggle_edit_mode()
            return True
            
        # If in edit mode, handle editor events
        if self.edit_mode:
            return self._handle_editor_event(event)
            
        # Otherwise, route to UI hierarchy
        return self.root.handle_event(event)
        
    def toggle_edit_mode(self) -> None:
        """Toggle edit mode on/off"""
        self.edit_mode = not self.edit_mode
        # Toggle debug flag on all elements
        self.root.set_child("debug")
        print(f"UI Edit Mode: {'ON' if self.edit_mode else 'OFF'}")
        
    def _handle_editor_event(self, event: pygame.event.Event) -> bool:
        """Handle events when in edit mode"""
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.KEYDOWN:
            # Ctrl+S: Save layout
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.save_layout_to_file()
                return True
            # Ctrl+T: Save UI tree (debug)
            if event.key == pygame.K_t and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self._save_tree_debug()
                return True
                
        # Mouse button down: select element
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            found = self._find_element_under_mouse(self.root, mouse_pos)
            if found and found != self.root:  # Don't select root
                self.selected_element = found
                self.offset_x = mouse_pos[0] - found.rect.x
                self.offset_y = mouse_pos[1] - found.rect.y
                return True
                
        # Mouse move: drag selected element
        elif event.type == pygame.MOUSEMOTION:
            if self.selected_element:
                new_x = mouse_pos[0] - self.offset_x
                new_y = mouse_pos[1] - self.offset_y
                # Snap to 5px grid for clean positioning
                self.selected_element.rect.x = round(new_x / 5) * 5
                self.selected_element.rect.y = round(new_y / 5) * 5
                return True
                
        # Mouse button up: release element
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.selected_element:
                # Optional: log new position
                # el = self.selected_element
                # print(f"Position for {el.uid}: x={el.rect.x}, y={el.rect.y}")
                self.selected_element = None
                return True
                
        return False
        
    def _find_element_under_mouse(self, parent: UIElement, pos: tuple[int, int]) -> Optional[UIElement]:
        """Find the topmost visible element under mouse position"""
        if not parent.visible:
            return None
            
        # Check children first (back-to-front)
        for child in reversed(parent.children):
            if child.visible:
                # Recursively check children
                found = self._find_element_under_mouse(child, pos)
                if found:
                    return found
                # Then check the child itself
                if child.get_screen_rect().collidepoint(pos):
                    return child
                    
        # Finally check parent itself
        if parent.get_screen_rect().collidepoint(pos):
            return parent
        return None
        
    def _save_tree_debug(self) -> None:
        """Save UI tree structure for debugging"""
        def collect_tree(element: UIElement, depth: int = 0) -> dict:
            result = {"uid": element.uid, "type": element.type, "children": []}
            for child in element.children:
                result["children"].append(collect_tree(child, depth + 1))
            return result
            
        import json
        tree_data = collect_tree(self.root)
        filename = f"ui_tree_{pygame.time.get_ticks()}.json"
        try:
            with open(filename, "w") as f:
                json.dump(tree_data, f, indent=2)
            print(f"UI tree saved to {filename}")
        except OSError:
            print("Failed to save UI tree")

    # ==========================
    # Game Loop Integration
    # ==========================

    def update(self, dt: float) -> None:
        """Update the UI hierarchy"""
        self.root.update(dt)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the UI hierarchy"""
        self.root.draw(surface)
        
    # ==========================
    # Helper Properties
    # ==========================

    @property
    def event_bus(self) -> Optional[Any]:
        """Get injected event bus"""
        return self._event_bus
        
    @property
    def panel_factory(self) -> Optional[Callable]:
        """Get injected panel factory"""
        return self._panel_factory
        
    @property
    def sprite_manager(self) -> Optional[Any]:
        """Get injected sprite manager"""
        return self._sprite_manager
        
    @property
    def save_manager(self) -> Optional[Any]:
        """Get injected save manager"""
        return self._save_manager