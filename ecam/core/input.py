def _normalize_key(key: str) -> str:
    """rendercanvas renvoie " " pour la touche Espace : on lui donne un nom stable."""
    return "Space" if key == " " else key


class InputManager:

    def __init__(self):
        # Touches actuellement maintenues enfoncées
        self._keys_down: set[str] = set()
        # Touches pressées UNIQUEMENT pendant la frame en cours
        self._keys_just_pressed: set[str] = set()
        # Touches relâchées UNIQUEMENT pendant la frame en cours
        self._keys_just_released: set[str] = set()

        # Souris
        self.mouse_x: float = 0.0
        self.mouse_y: float = 0.0
        self._mouse_down: set[int] = set()
        self._mouse_just_pressed: set[int] = set()

    def bind_to_canvas(self, canvas):
        """Attache les écouteurs d'événements à la fenêtre RenderCanvas."""

        @canvas.add_event_handler(
            "key_down", "key_up", "pointer_down", "pointer_up", "pointer_move"
        )
        def on_event(event):
            event_type = event.get("event_type")

            # --- CLAVIER ---
            if event_type == "key_down":
                key = _normalize_key(event.get("key"))
                if key not in self._keys_down:
                    self._keys_just_pressed.add(key)
                self._keys_down.add(key)

            elif event_type == "key_up":
                key = _normalize_key(event.get("key"))
                self._keys_down.discard(key)
                self._keys_just_released.add(key)

            # --- SOURIS ---
            elif event_type == "pointer_move":
                self.mouse_x = event.get("x")
                self.mouse_y = event.get("y")

            elif event_type == "pointer_down":
                btn = event.get("button")  # 1 = gauche, 2 = milieu, 3 = droite
                if btn not in self._mouse_down:
                    self._mouse_just_pressed.add(btn)
                self._mouse_down.add(btn)

            elif event_type == "pointer_up":
                btn = event.get("button")
                self._mouse_down.discard(btn)

    def is_key_down(self, key: str) -> bool:
        """Vrai tant que la touche reste enfoncée."""
        return key in self._keys_down

    def just_pressed(self, key: str) -> bool:
        """Vrai une seule fois lors de la frame où la touche est pressée."""
        return key in self._keys_just_pressed

    def just_released(self, key: str) -> bool:
        """Vrai une seule fois lors de la frame où la touche est relâchée."""
        return key in self._keys_just_released

    def is_mouse_down(self, button: int = 1) -> bool:
        """1 = Clic gauche, 2 = Clic molette, 3 = Clic droit."""
        return button in self._mouse_down

    def mouse_just_pressed(self, button: int = 1) -> bool:
        return button in self._mouse_just_pressed

    def clear_frame_inputs(self):
        """Doit être appelé à la fin de chaque frame pour vider les événements 'one-shot'."""
        self._keys_just_pressed.clear()
        self._keys_just_released.clear()
        self._mouse_just_pressed.clear()