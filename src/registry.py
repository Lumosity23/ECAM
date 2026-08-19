import numpy as np
from typing import Any

UINT8  = np.uint8
UINT32 = np.uint32
UINT64 = np.uint64

FLOAT16  = np.float16
FLOAT32  = np.float32
FLOAT128 = np.float128


class Registry:

    UINT8  = np.uint8
    UINT32 = np.uint32
    UINT64 = np.uint64

    FLOAT16  = np.float16
    FLOAT32  = np.float32
    FLOAT128 = np.float128

    def __init__(self, MAX_ENTITIES: int = 10000):
        self.MAX_ENTITIES = MAX_ENTITIES
        self.count: int = 0
        self.signatures = self._GetArrayZeros(UINT32)
        self.components: dict[str, np.ndarray] = {}
        self.masks: dict[str, int] = {}
        self.spatial_grid = None
        self.cell_size: int = 0
        self.SG_init: bool = False


    def _GetArrayZeros(self, type, shape: tuple = ()) -> np.ndarray :
        final_shape = (self.MAX_ENTITIES, *shape)
        return np.zeros(final_shape, dtype=type)
    

    def _UpdateSignature(self, id: UINT32, MASK: int):
        self.signatures[id] |= MASK


    def _Swap2End(self, id: UINT32, array: np.ndarray):
        last_id = self.count - 1
        array[id] = array[last_id]


    def _IsSpatialGrid(self) -> None:
        if not self.SG_init:
            raise SystemError("[ERROR] : La grid n'as pas ete init, veuilliez la config via la methode <SetSpacialGird>")


    def RegisterComponent(self, name: str, dtype: np.dtype, shape: tuple = ()):
        """ Register a new component for the ecs """
        array_component = self._GetArrayZeros(dtype, shape)
        mask_component = 1 << len(self.masks)

        self.components[name] = array_component
        self.masks[name] = mask_component


    def CreateEntity(self, entity_signature) -> int:
        """ Create a new entity """
        if self.count >= self.MAX_ENTITIES: return -1

        id = self.count
        self.signatures[id] = entity_signature
        self.count += 1
        return id
    

    def AddComponent(self, id: UINT32, *bundle_component_n_value: tuple[str, Any]) -> None:
        for name, value in bundle_component_n_value:
            if name in self.components:
                self.components[name][id] = value
                self._UpdateSignature(id, self.masks[name])

            else : raise ValueError(f"[ERROR] Component '{name}' does not exist!")


    def GetMask(self, *component_name: str) -> int:
        mask = 0
        for name in component_name:
            if name in self.masks:
                mask |= self.masks[name]
            else:
                raise ValueError(f"[ERROR] Component '{name}' does not exist!")
        return mask
    

    def Query(self, mask: np.uint32) -> np.ndarray:
        active_signatures = self.signatures[:self.count]
        return ( active_signatures & mask ) == mask
    
    
    def View(self, mask: np.uint32, *component_name: str) -> tuple[np.ndarray]:
        is_valid = self.Query(mask)
        arrays = tuple(self.components[name][:self.count] for name in component_name)
        return (is_valid, *arrays)


    def DestroyEntity(self, id: int) -> None:
        if id < 0 or id >= self.count:
            return 

        for array in self.components.values():
            self._Swap2End(id, array)
        
        self._Swap2End(id, self.signatures)

        self.count -= 1

    
    def SetSpacialGrid(self, cell_size: int = 50):
        self.spatial_grid = {}
        self.cell_size: int = cell_size
        self.SG_init = True

        # On finis pas mettre a jour la grid
        self.UpdateSpatialGrid()


    def UpdateSpatialGrid(self, cell_size: int = 50) -> None:
        self._IsSpatialGrid()
        self.cell_size = cell_size
        self.spatial_grid.clear()

        MASK_TRANSFORM = self.GetMask("Transform")
        
        is_valid, transforms = self.View(MASK_TRANSFORM, "Transform")
        valid_ids = np.where(is_valid)[0]
        cells = (transforms[is_valid] // cell_size).astype(int)
        
        for id, cell in zip(valid_ids, cells):
            cell_tuple = tuple(cell)
            self.spatial_grid.setdefault(cell_tuple, []).append(id)


    def GetEntitiesInChunk(self, cx: int, cy: int) -> list[UINT32]:
        self._IsSpatialGrid()
        return self.spatial_grid.get((cx, cy), [])
        
    
    def GetEntitiesAround(self, cx: int, cy: int, radius: int) -> list[list[UINT32]]:
        self._IsSpatialGrid()
        directions = [(x,y) for y in range(-radius, radius + 1) for x in range(-radius, radius + 1)]
        return [self.GetEntitiesInChunk(cx+x, cy+y) for x, y in directions if self.GetEntitiesInChunk(cx, cy) is not None]
        