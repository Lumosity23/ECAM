import pygame as pg
from dataclasses import dataclass

@dataclass
class KeyType:

    def __init__(self, key: str):
        self.key = key
        self.pg_key = f"K_{key}"
        
    

class InputManager:

    def __init__(self):
        self.key_map: dict[str, KeyType] = {}
        self.config: dict = {} # Ajourtera plus tard un loader de config

    
    def BindKey(self, key: str, action: str) -> None:
        """ Bind a key with an action """
        self.key_map[action] = KeyType(key)
    
    
    def IsPressed(self, action) -> bool:
        """ Verify is a key is pressed """
        if action in self.key_map:
            key = self.key_map[action]
            for event in pg.event.get():
                if event.type == key.pg_key:
                    return True
        return False
    
