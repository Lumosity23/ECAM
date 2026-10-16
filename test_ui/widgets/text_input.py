"""
UIInput - Single-line text input field
"""

from typing import TYPE_CHECKING, Optional, Callable
import pygame

from pygame_ui.core.ui_element import UIElement
from pygame_ui.widgets.text import UIText

if TYPE_CHECKING:
    import pygame.font

CURSOR_BLINK_SECONDS = 0.5


class UIInput(UIElement):
    """
    Single-line text field. Click it to focus, type to edit.

    Features:
    - Placeholder text shown while empty
    - Blinking cursor while focused
    - Long text scrolls so the end (cursor) stays visible, clipped to the field
    - Optional max length
    - Callbacks: on_change(text) on every edit, on_submit(text) on Enter
    - Escape or a click outside removes focus

    Keyboard events are consumed while focused, so game shortcuts do not fire while typing.
    """

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        placeholder: str = "",
        text: str = "",
        size_text: int = 30,
        text_color: tuple[int, int, int] = (255, 255, 255),
        placeholder_color: tuple[int, int, int] = (120, 120, 130),
        bg_color: tuple[int, int, int] = (40, 40, 50),
        focus_color: tuple[int, int, int] = (90, 140, 220),
        border_radius: int = 8,
        max_length: Optional[int] = None,
        on_change: Optional[Callable[[str], None]] = None,
        on_submit: Optional[Callable[[str], None]] = None,
        uid: Optional[str] = None
    ):
        """
        Initialize UIInput.

        Args:
            x, y: Top-left position
            w, h: Width and height
            placeholder: Text shown while the field is empty
            text: Initial text
            size_text: Font size
            text_color: Color of the typed text
            placeholder_color: Color of the placeholder
            bg_color: Background color
            focus_color: Border color while focused
            border_radius: Corner radius in pixels
            max_length: Maximum number of characters (None for no limit)
            on_change: Called with the new text after every edit
            on_submit: Called with the text when Enter is pressed
            uid: Unique identifier for layout loading
        """
        self.uid = uid
        self.type = "input"
        self.placeholder = placeholder
        self.size_text = size_text
        self.text_color = text_color
        self.placeholder_color = placeholder_color
        self.bg_color = bg_color
        self.focus_color = focus_color
        self.border_radius = border_radius
        self.max_length = max_length
        self.on_change = on_change
        self.on_submit = on_submit
        self.padding = 10

        self.value = ""
        self.focused = False
        self._blink_time = 0.0
        self._cursor_visible = True

        super().__init__(x, y, w, h, uid)

        # Internal label (no uid: it is positioned by the field, not by the layout file)
        self.label = UIText(0, 0, "", size_text, text_color)
        self.add_child(self.label)

        self.set_text(text)

    # ==========================
    # Public API
    # ==========================

    def get_text(self) -> str:
        """Current text (the placeholder is never returned)"""
        return self.value

    def set_text(self, text: str) -> None:
        """Replace the text programmatically. Does not call on_change."""
        self.value = self._limit(text)
        self._render()

    def clear(self) -> None:
        """Empty the field. Does not call on_change."""
        self.set_text("")

    def focus(self) -> None:
        """Give the field keyboard focus"""
        self._set_focus(True)

    def blur(self) -> None:
        """Remove keyboard focus"""
        self._set_focus(False)

    # ==========================
    # Internals
    # ==========================

    def _limit(self, text: str) -> str:
        """Cut text to max_length if one is set"""
        if self.max_length is not None:
            return text[:self.max_length]
        return text

    def _set_focus(self, focused: bool) -> None:
        if focused == self.focused:
            return
        self.focused = focused
        self._blink_time = 0.0
        self._cursor_visible = True
        if focused:
            # Pygame only sends TEXTINPUT events while text input is enabled
            pygame.key.start_text_input()
        self._render()

    def _insert(self, text: str) -> None:
        room = len(text) if self.max_length is None else self.max_length - len(self.value)
        if room <= 0 or not text:
            return
        self.value += text[:room]
        self._changed()

    def _delete_last(self) -> None:
        if not self.value:
            return
        self.value = self.value[:-1]
        self._changed()

    def _changed(self) -> None:
        self._cursor_visible = True
        self._blink_time = 0.0
        self._render()
        if self.on_change:
            self.on_change(self.value)

    def _render(self) -> None:
        """Redraw the background, border, cursor and the (scrolled) label"""
        w, h = self.rect.size
        pad = self.padding
        radius = self.border_radius
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Background (through the panel factory when one is set)
        if self.panel_factory:
            self.image.blit(self.panel_factory(w, h, self.bg_color), (0, 0))
        else:
            pygame.draw.rect(self.image, self.bg_color, self.image.get_rect(), border_radius=radius)

        if self.focused:
            pygame.draw.rect(self.image, self.focus_color, self.image.get_rect(), width=2, border_radius=radius)

        # Label: placeholder when empty, otherwise the text
        if self.value:
            self.label.set_text(self.value, color=self.text_color)
        else:
            self.label.set_text(self.placeholder, color=self.placeholder_color)

        text_w, text_h = self.label.image.get_size()
        inner_w = w - 2 * pad

        # Scroll so that the end of long text stays visible
        offset = min(0, inner_w - text_w) if self.value else 0
        self.label.rect.x = pad + offset
        self.label.rect.y = (h - text_h) // 2

        # Cursor, drawn under the label, only while focused and in the visible phase of the blink
        if self.focused and self._cursor_visible:
            cursor_x = pad + min(text_w + offset, inner_w) if self.value else pad
            cursor_top = (h - text_h) // 2 + 2
            pygame.draw.line(
                self.image,
                self.text_color,
                (cursor_x, cursor_top),
                (cursor_x, cursor_top + text_h - 4),
                2,
            )

    def _on_layout_applied(self) -> None:
        """Layout loaded or size changed: redraw at the new size"""
        self._render()

    # ==========================
    # Game loop / events
    # ==========================

    def update(self, dt: float) -> None:
        """Blink the cursor while focused"""
        super().update(dt)
        if not self.focused:
            return
        self._blink_time += dt
        if self._blink_time >= CURSOR_BLINK_SECONDS:
            self._blink_time -= CURSOR_BLINK_SECONDS
            self._cursor_visible = not self._cursor_visible
            self._render()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle focus and typing.

        Returns True if the event was used by the field.
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            inside = self.get_screen_rect().collidepoint(event.pos)
            self._set_focus(inside)
            return inside

        if not self.focused:
            return False

        if event.type == pygame.TEXTINPUT:
            self._insert(event.text)
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._delete_last()
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.on_submit:
                    self.on_submit(self.value)
                return True
            if event.key == pygame.K_ESCAPE:
                self._set_focus(False)
                return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the field, clipping its label to the field area"""
        if not self.visible:
            return

        abs_rect = self.get_screen_rect()
        surface.blit(self.image, abs_rect)

        old_clip = surface.get_clip()
        surface.set_clip(abs_rect)
        for child in self.children:
            child.draw(surface)
        surface.set_clip(old_clip)

        if self.debug:
            pygame.draw.rect(surface, (255, 0, 255), abs_rect, 2)
