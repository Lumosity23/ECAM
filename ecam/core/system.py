from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .registry import Registry


class System(ABC):

    def __init__(self, registry: "Registry"):
        self.registry = registry
        self.enabled: bool = True


    @abstractmethod
    def update(self, dt: float) -> None:
        """Méthode exécutée à chaque frame logique."""
        pass