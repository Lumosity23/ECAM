from collections import deque
from contextlib import contextmanager
import time


class Profiler:

    def __init__(self, history_size: int = 60):
        # Stocke les 60 dernières mesures pour chaque section
        self._history: dict[str, deque[float]] = {}
        self._averages: dict[str, float] = {}

    @contextmanager
    def measure(self, name: str):
        """Mesure le temps d'exécution d'un bloc de code (en millisecondes).

        Utilisation : with profiler.measure("Logique"): ...
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            if name not in self._history:
                self._history[name] = deque(maxlen=60)

            self._history[name].append(elapsed_ms)
            # Moyenne lissée sur les 60 dernières frames
            self._averages[name] = sum(self._history[name]) / len(
                self._history[name]
            )

    def get_ms(self, name: str) -> float:
        """Retourne le temps moyen lissé d'une section en ms."""
        return self._averages.get(name, 0.0)

    def summary(self) -> str:
        """Génère une ligne de résumé propre."""
        return " | ".join(
            [f"{k}: {v:.2f}ms" for k, v in self._averages.items()]
        )