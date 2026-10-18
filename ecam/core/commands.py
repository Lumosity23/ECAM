from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .registry import Registry
    from .types import EntityID


class Commands:
    """
    File d'attente d'opérations "dangereuses" à exécuter plus tard, à un moment sûr.

    LE PROBLÈME
    Un système itère sur des tableaux numpy en utilisant des INDEX. Or détruire une
    entité déclenche un swap-remove : la dernière entité vient prendre la place de
    celle qu'on supprime, donc tous les index calculés avant deviennent faux.
    Détruire "en direct" pendant qu'un système travaille, c'est scier la branche
    sur laquelle il est assis.

    LA SOLUTION
    Au lieu de détruire tout de suite, un système écrit une demande :

        registry.commands.despawn(eid)        # "détruis-la, mais pas maintenant"

    et le Registry appelle `apply()` entre deux étages, quand plus aucun système
    n'est en train d'itérer.

    Règle : CRÉER librement (une nouvelle entité va en fin de tableau, elle ne
    déplace personne), mais DÉTRUIRE via les commandes.
    """

    def __init__(self, registry: "Registry"):
        self._registry = registry
        # Chaque entrée : (fonction à appeler, tuple d'arguments)
        self._queue: list[tuple[Callable[..., Any], tuple]] = []


    def despawn(self, eid: "EntityID") -> None:
        """ Demande la destruction d'une entité (exécutée au prochain apply). """
        # destroy_entity renvoie False sans rien casser si l'id est déjà mort :
        # demander deux fois la même destruction est donc sans danger.
        self._queue.append((self._registry.destroy_entity, (eid,)))


    def remove_component(self, eid: "EntityID", *names: str) -> None:
        """ Demande le retrait de composants/tags (exécuté au prochain apply). """
        # --- À TOI DE JOUER (1/4) -------------------------------------------
        # Copie le principe de `despawn` juste au-dessus : on empile un couple
        # (fonction, arguments) dans self._queue.
        # Attention : n'empile PAS registry.remove_component directement. Si
        # l'entité est détruite par une autre commande avant la nôtre,
        # registry.remove_component lèverait une erreur. Utilise plutôt le
        # helper _remove_if_alive défini plus bas : il vérifie d'abord.
        raise NotImplementedError("Commands.remove_component : à implémenter")


    def _remove_if_alive(self, eid: "EntityID", names: tuple[str, ...]) -> None:
        """ Helper : retire les composants seulement si l'entité existe encore. """
        if self._registry.is_alive(eid):
            self._registry.remove_component(eid, *names)


    def apply(self) -> None:
        """ Exécute toutes les demandes en attente, dans l'ordre où elles ont été faites. """
        # On vide la file AVANT d'exécuter : si une commande en déclenche une autre,
        # celle-ci attendra le prochain apply au lieu de boucler à l'infini.
        queue, self._queue = self._queue, []
        for function, args in queue:
            function(*args)


    def __len__(self) -> int:
        """ Nombre de demandes en attente (pratique pour les tests). """
        return len(self._queue)
