import numpy as np
from .types import UINT32, INT32, EntityID
from .system import System
from typing import Any


class Registry:


    def __init__(self, MAX_ENTITIES: int = 10000):
        self.MAX_ENTITIES = MAX_ENTITIES
        self.count: int = 0
        self.next_entity_id = 0
        self.signatures = self._get_array_zeros(UINT32)
        self.components: dict[str, np.ndarray] = {}
        self.masks: dict[str, UINT32] = {}
        self.dense = self._get_array_zeros(UINT32)
        self.sparse = self._get_array_zeros(INT32)
        self.free_ids: list[EntityID] = []

        self.systems: list[System] = []
        

    def _get_array_zeros(self, type, shape: tuple = ()) -> np.ndarray :
        """ Get a numpy array with a lenght of MAX_ENTITIES with zeros """
        final_shape = (self.MAX_ENTITIES, *shape)
        return np.zeros(final_shape, dtype=type)
    

    def _update_signature(self, id: UINT32, MASK: int):
        """ Update the signature of an entity """
        self.signatures[id] |= MASK


    def create_entity(self, entity_signature = 0 ) -> EntityID:
        """ Create a new entity """
        if self.count >= self.MAX_ENTITIES: return -1

        if self.free_ids:
            id = self.free_ids.pop()
        else:
            id = self.next_entity_id
            self.next_entity_id += 1

        dense_index = self.count
        self.dense[dense_index] = id
        self.sparse[id] = dense_index
        self.signatures[dense_index] = entity_signature
        self.count += 1
        return id
    

    def destroy_entity(self, id: int) -> None:
        """ Destroy a entity """
        if id < 0 or id >= self.MAX_ENTITIES:
            return 

        if self.sparse[id] == -1:
            return
        
        target_index = self.sparse[id]
        last_index = self.count - 1
        last_entity_id = self.dense[last_index]

        if target_index != last_index:

            for array in self.components.values():
                array[target_index] = array[last_index]

            self.signatures[target_index] = self.signatures[last_index]
            self.dense[target_index] = last_entity_id
            self.sparse[last_entity_id] = target_index
        
        self.sparse[id] = -1
        self.free_ids.append(id)
        self.count -= 1


    def register_component(self, name: str, dtype: np.dtype, shape: tuple = ()):
        """ Register a new component for the ecs """
        array_component = self._get_array_zeros(dtype, shape)
        mask_component = 1 << len(self.masks)

        self.components[name] = array_component
        self.masks[name] = mask_component


    def add_component(self, id: UINT32, *bundle_component_n_value: tuple[str, Any]) -> None:
        """ Add a component to a entity """
        if id < 0 or id >= self.MAX_ENTITIES or self.sparse[id] == -1:
            raise ValueError(f"[ERROR] Entity {id} does not exist or is destroyed!")

        target_index = self.sparse[id]
        for name, value in bundle_component_n_value:
            if name in self.components:
                self.components[name][target_index] = value
                self._update_signature(target_index, self.masks[name])

            else : raise ValueError(f"[ERROR] Component '{name}' does not exist!")

    
    def is_component_exist(self, component_name: str) -> bool:
        return component_name in self.components
    

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
    

    def get_mask(self, *component_name: str) -> UINT32:
        """ Get a mask of components """
        mask: UINT32 = 0
        for name in component_name:
            if name in self.masks:
                mask |= self.masks[name]
            else:
                raise ValueError(f"[ERROR] Component '{name}' does not exist!")
        return mask
    

    def query(self, mask: np.uint32) -> np.ndarray:
        """ Get the liste of the valid index base on a mask """
        active_signatures = self.signatures[:self.count]
        return ( active_signatures & mask ) == mask
    
    
    def view(self, mask: UINT32, *component_name: str) -> tuple[np.ndarray]:
        """ Get the liste og component and ID valid for a mask given """
        is_valid = self.query(mask)
        arrays = tuple(self.components[name][:self.count] for name in component_name)
        return (is_valid, *arrays)