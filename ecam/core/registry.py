import numpy as np
from .types import (
    UINT32, UINT64, INT32,
    EntityID, NULL_ENTITY, GENERATION_MASK,
    make_entity, slot_of, generation_of,
)
from .system import System
from typing import Any

# Les signatures sont des uint64 : 1 bit par composant (ou tag) => 64 maximum.
# (Si un jour ça ne suffit plus : passer à une matrice (N, K) de mots uint64.)
MAX_COMPONENTS = 64


class Registry:
    """
    Le "monde" ECS : entités + composants + systèmes.

    Stockage : Structure of Arrays (SoA).
    Chaque composant est UN tableau numpy de taille MAX_ENTITIES. Les entités
    vivantes sont rangées en tête de ces tableaux (indices 0..count-1), sans trou.
    """

    def __init__(self, MAX_ENTITIES: int = 10000):
        self.MAX_ENTITIES = MAX_ENTITIES
        self.count: int = 0
        self.next_slot: int = 0

        # --- Tableaux indexés par INDEX (position dense) ---
        self.signatures = self._get_array_zeros(UINT64)  # quels composants a l'entité
        self.dense = self._get_array_zeros(UINT32)       # index -> slot

        # --- Tableaux indexés par SLOT (identité stable) ---
        # -1 = "ce slot n'est pas occupé" (avant : 0, ce qui était ambigu avec l'index 0)
        self.sparse = np.full(MAX_ENTITIES, -1, dtype=INT32)  # slot -> index
        self.generations = self._get_array_zeros(UINT32)      # slot -> génération actuelle

        self.free_slots: list[int] = []

        self.components: dict[str, np.ndarray] = {}
        self.masks: dict[str, np.uint64] = {}   # contient les composants ET les tags

        self.systems: list[System] = []


    def _get_array_zeros(self, type, shape: tuple = ()) -> np.ndarray:
        """ Get a numpy array with a lenght of MAX_ENTITIES with zeros """
        final_shape = (self.MAX_ENTITIES, *shape)
        if type is object:
            # Un composant "objet" peut contenir des str, des tuples, des fonctions...
            # On part de None plutôt que de 0.
            return np.full(final_shape, None, dtype=object)
        return np.zeros(final_shape, dtype=type)


    # ------------------------------------------------------------------
    # IDENTITÉ DES ENTITÉS
    # ------------------------------------------------------------------
    def is_alive(self, eid: EntityID) -> bool:
        """ Vrai si cet id désigne une entité vivante (et pas un id périmé). """
        eid = int(eid)
        if eid < 0:
            return False
        slot = slot_of(eid)
        if slot >= self.MAX_ENTITIES:
            return False
        # Deux conditions : le slot est occupé ET la génération correspond.
        return bool(self.sparse[slot] != -1 and self.generations[slot] == generation_of(eid))


    def index_of(self, eid: EntityID) -> int:
        """
        Position de l'entité dans les tableaux denses, ou -1 si elle est morte.
        C'est LA porte d'entrée pour lire/écrire un composant d'une entité précise.
        """
        if not self.is_alive(eid):
            return -1
        return int(self.sparse[slot_of(int(eid))])


    def entity_at(self, index: int) -> EntityID:
        """ L'opération inverse : quel EntityID occupe cette position dense ? """
        slot = int(self.dense[index])
        return make_entity(slot, int(self.generations[slot]))


    def create_entity(self, entity_signature=0) -> EntityID:
        """ Create a new entity """
        if self.count >= self.MAX_ENTITIES:
            return NULL_ENTITY

        if self.free_slots:
            slot = self.free_slots.pop()
        else:
            slot = self.next_slot
            self.next_slot += 1

        index = self.count
        self.dense[index] = slot
        self.sparse[slot] = index
        self.signatures[index] = entity_signature
        self.count += 1
        return make_entity(slot, int(self.generations[slot]))


    def destroy_entity(self, eid: EntityID) -> bool:
        """ Destroy a entity. Retourne False si l'id était déjà mort/invalide. """
        if not self.is_alive(eid):
            return False

        slot = slot_of(int(eid))
        target_index = int(self.sparse[slot])
        last_index = self.count - 1
        last_slot = int(self.dense[last_index])

        # SWAP-REMOVE : la dernière entité vient boucher le trou.
        if target_index != last_index:
            for array in self.components.values():
                array[target_index] = array[last_index]

            self.signatures[target_index] = self.signatures[last_index]
            self.dense[target_index] = last_slot
            self.sparse[last_slot] = target_index

        self.signatures[last_index] = 0
        self.sparse[slot] = -1

        # La génération avance : tous les anciens ids de ce slot deviennent morts.
        self.generations[slot] = (int(self.generations[slot]) + 1) & GENERATION_MASK
        self.free_slots.append(slot)
        self.count -= 1
        return True


    # ------------------------------------------------------------------
    # COMPOSANTS ET TAGS
    # ------------------------------------------------------------------
    def _alloc_mask(self, name: str) -> np.uint64:
        """
        Réserve le prochain bit libre de la signature pour `name`.
        Partagé par les composants ET les tags (qui n'ont pas de tableau).
        """
        if name in self.masks:
            raise ValueError(f"[ERROR] '{name}' is already registered!")
        if len(self.masks) >= MAX_COMPONENTS:
            raise ValueError(f"[ERROR] Cannot register '{name}': {MAX_COMPONENTS} components max!")

        mask = np.uint64(1) << np.uint64(len(self.masks))
        self.masks[name] = mask
        return mask


    def register_component(self, name: str, dtype: np.dtype, shape: tuple = ()):
        """
        Register a new component for the ecs.
        dtype=object est accepté (textes, callbacks...) mais seulement avec shape=().
        """
        if dtype is object and shape != ():
            raise ValueError("[ERROR] An object component must have shape ()")

        self._alloc_mask(name)  # lève une erreur si le nom existe déjà
        self.components[name] = self._get_array_zeros(dtype, shape)


    def register_tag(self, name: str) -> None:
        """
        Register a tag : un composant SANS donnée, juste un bit dans la signature.
        Exemples d'usage plus tard : "Node" (fait partie de l'UI), "Hidden"...
        """
        # --- À TOI DE JOUER (1/3) -------------------------------------------
        # Regarde register_component juste au-dessus : un tag, c'est pareil,
        # sauf qu'on ne crée PAS de tableau dans self.components.
        # Indice : une seule ligne suffit, avec la méthode _alloc_mask.
        raise NotImplementedError("register_tag : à implémenter (voir le commentaire)")


    def add_component(self, eid: EntityID, *bundle) -> None:
        """
        Add components (and/or tags) to an entity.
        Chaque élément du bundle est soit ("Nom", valeur), soit "Nom" tout seul (tag).
        """
        index = self.index_of(eid)
        if index == -1:
            raise ValueError(f"[ERROR] Entity {eid} does not exist or is destroyed!")

        for item in bundle:
            name, value = (item, None) if isinstance(item, str) else item

            if name not in self.masks:
                raise ValueError(f"[ERROR] Component '{name}' does not exist!")

            if name in self.components:        # un tag n'a pas de tableau : rien à écrire
                self.components[name][index] = value

            self.signatures[index] |= self.masks[name]


    def remove_component(self, eid: EntityID, *names: str) -> None:
        """ Remove components (and/or tags) from an entity. """
        index = self.index_of(eid)
        if index == -1:
            raise ValueError(f"[ERROR] Entity {eid} does not exist or is destroyed!")

        for name in names:
            if name not in self.masks:
                raise ValueError(f"[ERROR] Component '{name}' does not exist!")

            # ATTENTION : pour éteindre un bit on fait  sig & (~mask).
            # Ça ne marche que si mask est un np.uint64 : avec un int Python,
            # ~mask serait négatif et numpy refuserait de le mélanger à de l'uint64.
            self.signatures[index] &= ~self.masks[name]

            # Un composant objet : on lâche la référence pour que Python libère l'objet.
            if name in self.components and self.components[name].dtype == object:
                self.components[name][index] = None


    def has_component(self, eid: EntityID, name: str) -> bool:
        """ Vrai si l'entité (vivante) possède ce composant ou ce tag. """
        # --- À TOI DE JOUER (2/3) -------------------------------------------
        # 1. Retrouve l'index de l'entité (méthode index_of). Si elle est morte
        #    (-1), la réponse est False.
        # 2. Vérifie que `name` existe dans self.masks (sinon : ValueError,
        #    comme dans add_component).
        # 3. Teste le bit :  (self.signatures[index] & self.masks[name]) != 0
        #    Pense à renvoyer un vrai bool Python : bool(...)
        raise NotImplementedError("has_component : à implémenter (voir le commentaire)")


    def get_component(self, eid: EntityID, name: str):
        """
        Donne la valeur du composant de CETTE entité.
        Pour un composant de forme (2,) on récupère une VUE : modifier le résultat
        modifie le tableau (c'est voulu, c'est le même principe que `view`).
        """
        # --- À TOI DE JOUER (3/3) -------------------------------------------
        # Même début que has_component. Si l'entité n'a pas le composant,
        # lève une ValueError. Sinon renvoie self.components[name][index].
        # Réfléchis : que faut-il faire pour un tag (pas de tableau) ?
        raise NotImplementedError("get_component : à implémenter (voir le commentaire)")


    def is_component_exist(self, component_name: str) -> bool:
        """ Un composant OU un tag enregistré. """
        return component_name in self.masks


    # ------------------------------------------------------------------
    # SYSTÈMES
    # ------------------------------------------------------------------
    def add_system(self, system: System) -> System:
        """ Add a system to the register """
        self.systems.append(system)
        return system


    def update_systems(self, dt) -> None:
        """ Call the update methode of all systems enabled """
        for system in self.systems:
            if system.enabled:
                system.update(dt)


    def get_system[T: System](self, system_type: type[T]) -> T | None:
        """ Get a systems register with the name """
        for system in self.systems:
            if isinstance(system, system_type):
                return system
        return None


    # ------------------------------------------------------------------
    # REQUÊTES
    # ------------------------------------------------------------------
    def get_mask(self, *component_name: str) -> np.uint64:
        """ Get a mask of components """
        mask = np.uint64(0)
        for name in component_name:
            if name in self.masks:
                mask |= self.masks[name]
            else:
                raise ValueError(f"[ERROR] Component '{name}' does not exist!")
        return mask


    def query(self, mask: np.uint64) -> np.ndarray:
        """ Get the liste of the valid index base on a mask """
        active_signatures = self.signatures[:self.count]
        return (active_signatures & mask) == mask


    def view(self, mask: np.uint64, *component_name: str) -> tuple[np.ndarray, ...]:
        """ Get the liste og component and ID valid for a mask given """
        is_valid = self.query(mask)
        arrays = tuple(self.components[name][:self.count] for name in component_name)
        return (is_valid, *arrays)
