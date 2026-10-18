import numpy as np
from .types import (
    UINT32, UINT64, INT32,
    EntityID, NULL_ENTITY, GENERATION_MASK,
    make_entity, slot_of, generation_of,
)
from .system import System
from .commands import Commands
from typing import Any

# Étages par défaut d'une frame, dans l'ordre d'exécution.
# Un système sans précision va dans "update". On pourra en insérer d'autres
# (ex : les étages de l'UI) avec Registry.add_stage.
DEFAULT_STAGES = ("input", "update", "post_update")

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

        # --- Organisation de la frame ---
        self.stages: list[str] = list(DEFAULT_STAGES)               # ordre d'exécution
        self.systems: dict[str, list[System]] = {s: [] for s in self.stages}

        # Singletons du monde (voir la section RESSOURCES) : un objet par type.
        self.resources: dict[type, Any] = {}

        # Demandes différées (despawn...) exécutées entre deux étages.
        self.commands = Commands(self)


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
        self._alloc_mask(name)


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

            self.signatures[index] &= ~self.masks[name]

            # Un composant objet : on lâche la référence pour que Python libère l'objet.
            if name in self.components and self.components[name].dtype == object:
                self.components[name][index] = None


    def has_component(self, eid: EntityID, name: str) -> bool:
        """ Vrai si l'entité (vivante) possède ce composant ou ce tag. """
        index = self.index_of(eid)
        if index == -1:
            return False
        
        if name not in self.masks:
            raise ValueError(f"[ERROR] Component '{name}' does not exist!")

        return bool((self.signatures[index] & self.masks[name]) != 0)


    def get_component(self, eid: EntityID, name: str):
        """
        Donne la valeur du composant de CETTE entité.
        Pour un composant de forme (2,) on récupère une VUE : modifier le résultat
        modifie le tableau (c'est voulu, c'est le même principe que `view`).
        """
        index = self.index_of(eid)

        if not self.has_component(eid, name):
            raise ValueError(f"[ERROR] Entity {eid} does not have this component : {name}")
        
        # Réfléchis : que faut-il faire pour un tag (pas de tableau) ?
        return self.components[name][index]
    

    def is_component_exist(self, component_name: str) -> bool:
        """ Un composant OU un tag enregistré. """
        return component_name in self.masks


    # ------------------------------------------------------------------
    # SYSTÈMES
    # ------------------------------------------------------------------
    def add_stage(self, name: str, *, after: str | None = None, before: str | None = None) -> None:
        """
        Crée un nouvel étage, placé juste après `after` ou juste avant `before`
        (à la fin si on ne précise rien). Exemple : add_stage("ui_layout", after="update").
        """
        # --- À TOI DE JOUER (2/4) -------------------------------------------
        # self.stages est une liste de noms : l'ORDRE de la liste est l'ordre
        # d'exécution. Il faut :
        #   1. refuser un nom qui existe déjà (ValueError)
        #   2. refuser after ET before donnés en même temps (ValueError)
        #   3. calculer la position d'insertion :
        #        after  -> self.stages.index(after) + 1
        #        before -> self.stages.index(before)
        #        rien   -> len(self.stages)
        #      (index() lève déjà une ValueError si le nom n'existe pas : parfait)
        #   4. self.stages.insert(position, name)
        #   5. ne pas oublier de créer la liste de systèmes de ce nouvel étage :
        #        self.systems[name] = []
        raise NotImplementedError("add_stage : à implémenter (voir le commentaire)")


    def add_system(self, system: System, stage: str = "update") -> System:
        """ Add a system to the register, in the given stage """
        if stage not in self.systems:
            raise ValueError(f"[ERROR] Stage '{stage}' does not exist! Known stages: {self.stages}")
        self.systems[stage].append(system)
        return system


    def update_systems(self, dt) -> None:
        """ Call the update methode of all systems enabled, stage after stage """
        for stage in self.stages:
            for system in self.systems[stage]:
                if system.enabled:
                    system.update(dt)

            # Fin d'étage : plus aucun système n'itère, c'est le moment SÛR pour
            # exécuter les despawn demandés pendant cet étage.
            self.commands.apply()


    def get_system[T: System](self, system_type: type[T]) -> T | None:
        """ Get a systems register with the name """
        for stage in self.stages:
            for system in self.systems[stage]:
                if isinstance(system, system_type):
                    return system
        return None


    # ------------------------------------------------------------------
    # RESSOURCES : des singletons du monde
    # ------------------------------------------------------------------
    # Une ressource est un objet UNIQUE auquel tous les systèmes ont accès, et qui
    # n'appartient à aucune entité : l'état de la souris, le thème de l'UI, la
    # taille de l'écran... On la retrouve par son TYPE (comme get_system).
    def insert_resource[T](self, resource: T) -> T:
        """ Enregistre une ressource. Une ressource du même type est remplacée. """
        self.resources[type(resource)] = resource
        return resource


    def has_resource(self, resource_type: type) -> bool:
        """ Vrai si une ressource de ce type est enregistrée. """
        return resource_type in self.resources


    def get_resource[T](self, resource_type: type[T]) -> T:
        """ Retourne la ressource de ce type. Lève KeyError si elle n'existe pas. """
        # --- À TOI DE JOUER (3/4) -------------------------------------------
        # Regarde insert_resource : la clé du dictionnaire est le type.
        # Contrairement à get_system (qui renvoie None), une ressource absente est
        # presque toujours un oubli d'initialisation : on préfère PLANTER avec un
        # message clair plutôt que de propager un None qui explosera plus loin.
        # Lève une KeyError dont le message contient le nom du type
        # (resource_type.__name__).
        raise NotImplementedError("get_resource : à implémenter (voir le commentaire)")


    def remove_resource[T](self, resource_type: type[T]) -> T | None:
        """ Retire la ressource de ce type et la renvoie (None si elle n'existait pas). """
        # --- À TOI DE JOUER (4/4) -------------------------------------------
        # Une seule ligne avec dict.pop et une valeur par défaut.
        raise NotImplementedError("remove_resource : à implémenter (voir le commentaire)")


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
