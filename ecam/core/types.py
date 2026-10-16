from typing import TypeAlias
import numpy as np

INT8 = np.int8
INT16 = np.int16
INT32 = np.int32
INT64 = np.int64

UINT8 = np.uint8
UINT16 = np.uint16
UINT32 = np.uint32
UINT64 = np.uint64

FLOAT16 = np.float16
FLOAT32 = np.float32

# ----------------------------------------------------------------------
# IDENTITÉ D'UNE ENTITÉ
# ----------------------------------------------------------------------
# Un EntityID est un entier Python "empaqueté" en deux morceaux :
#
#       EntityID  =  ( generation << 32 )  |  slot
#                      bits 32..62            bits 0..31
#
#   - slot       : le numéro de case stable (c'est l'ancien "id" de ton registry).
#   - generation : un compteur qui augmente chaque fois que le slot est détruit.
#
# Pourquoi ? Quand une entité est détruite, son slot est recyclé. Sans génération,
# un composant qui garde l'ancien id (ex : Parent) pointerait en silence vers la
# NOUVELLE entité qui occupe le slot. Avec la génération, l'ancien id devient
# simplement "mort" (voir Registry.is_alive).
#
# Vocabulaire à retenir (on le réutilisera partout) :
#   - slot  : partie stable de l'id (ne bouge jamais tant que l'entité vit)
#   - index : position de l'entité dans les tableaux denses (INSTABLE : le
#             swap-remove la déplace quand une autre entité est détruite)
EntityID: TypeAlias = int

NULL_ENTITY: EntityID = -1  # "aucune entité" (parent absent, cible vide...)

SLOT_BITS = 32
SLOT_MASK = (1 << SLOT_BITS) - 1
GENERATION_MASK = 0x7FFFFFFF  # 31 bits : l'id reste positif même dans un int64


def make_entity(slot: int, generation: int) -> EntityID:
    """Empaquette (slot, génération) en un seul EntityID."""
    return (generation << SLOT_BITS) | slot


def slot_of(eid: EntityID) -> int:
    """Extrait la partie stable (le slot) d'un EntityID."""
    return eid & SLOT_MASK


def generation_of(eid: EntityID) -> int:
    """Extrait la génération d'un EntityID."""
    return eid >> SLOT_BITS