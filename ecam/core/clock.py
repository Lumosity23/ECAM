import time


class Clock:

    def __init__(self):
        self._last_time: float = time.perf_counter()
        self._frame_count: int = 0
        self._accumulator: float = 0.0
        self._fps: float = 0.0

        # Fréquence de mise à jour du FPS (en secondes)
        self.update_interval: float = 0.5

    def tick(self) -> float:
        """Calcule le delta time (dt) et met à jour le compteur de FPS.

        Retourne :
            dt (float) : Le temps écoulé depuis la dernière frame en secondes.
        """
        now = time.perf_counter()
        dt = now - self._last_time
        self._last_time = now

        # On accumule le temps et on compte une frame de plus
        self._accumulator += dt
        self._frame_count += 1

        # Dès que l'intervalle est dépassé (ex: 0.5s), on calcule la moyenne
        if self._accumulator >= self.update_interval:
            self._fps = self._frame_count / self._accumulator
            # Réinitialisation pour la prochaine mesure
            self._frame_count = 0
            self._accumulator = 0.0

        return dt

    @property
    def fps(self) -> float:
        """Retourne le framerate stabilisé actuel."""
        return self._fps