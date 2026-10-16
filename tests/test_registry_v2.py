"""
Tests du Registry v2.

Lancer :   python tests/test_registry_v2.py
(ou `pytest tests/test_registry_v2.py` si tu installes pytest : les fonctions
 test_* sont au format pytest, mais un mini-lanceur est fourni en bas.)

Les tests marqués [EXERCICE] ne passent qu'une fois que tu as écrit
register_tag / has_component / get_component dans registry.py.
"""
import numpy as np

from ecam.core.registry import Registry, MAX_COMPONENTS
from ecam.core.types import FLOAT32, INT64, NULL_ENTITY, slot_of, generation_of


def make_world() -> Registry:
    world = Registry(MAX_ENTITIES=16)
    world.register_component("Pos", FLOAT32, (2,))
    world.register_component("Label", object)        # composant non numérique
    world.register_component("Parent", INT64)        # stocke un EntityID
    return world


# ----------------------------------------------------------------------
# Identité : slots, index, générations
# ----------------------------------------------------------------------
def test_create_and_alive():
    w = make_world()
    a = w.create_entity()
    assert w.is_alive(a)
    assert w.count == 1
    assert w.index_of(a) == 0
    assert w.entity_at(0) == a


def test_destroy_makes_id_dead_and_is_idempotent():
    w = make_world()
    a = w.create_entity()
    assert w.destroy_entity(a) is True
    assert not w.is_alive(a)
    assert w.index_of(a) == -1
    assert w.destroy_entity(a) is False      # déjà mort : rien ne se passe


def test_recycled_slot_gets_new_generation():
    w = make_world()
    a = w.create_entity()
    w.destroy_entity(a)
    b = w.create_entity()                    # réutilise le slot de a
    assert slot_of(b) == slot_of(a)
    assert generation_of(b) == generation_of(a) + 1
    assert w.is_alive(b)
    assert not w.is_alive(a)                 # l'ancien id ne désigne PAS b


def test_stale_id_cannot_modify_new_entity():
    w = make_world()
    a = w.create_entity()
    w.destroy_entity(a)
    w.create_entity()
    try:
        w.add_component(a, ("Pos", (1, 1)))
    except ValueError:
        return
    raise AssertionError("un id périmé ne doit pas pouvoir écrire")


def test_swap_remove_keeps_data_aligned():
    w = make_world()
    ids = [w.create_entity() for _ in range(4)]
    for n, eid in enumerate(ids):
        w.add_component(eid, ("Pos", (n, n * 10)))
    w.destroy_entity(ids[1])                 # une entité du milieu disparaît
    for n in (0, 2, 3):                      # les autres gardent leurs données
        i = w.index_of(ids[n])
        assert tuple(w.components["Pos"][i]) == (n, n * 10)
    assert w.count == 3


def test_world_full_returns_null_entity():
    w = make_world()
    for _ in range(16):
        assert w.create_entity() != NULL_ENTITY
    assert w.create_entity() == NULL_ENTITY


def test_sparse_starts_at_minus_one():
    w = make_world()
    assert (w.sparse == -1).all()


# ----------------------------------------------------------------------
# Composants
# ----------------------------------------------------------------------
def test_remove_component():
    w = make_world()
    a = w.create_entity()
    w.add_component(a, ("Pos", (1, 2)), ("Parent", 5))
    w.remove_component(a, "Pos")
    mask_pos = w.get_mask("Pos")
    mask_parent = w.get_mask("Parent")
    assert not w.query(mask_pos)[0]
    assert w.query(mask_parent)[0]           # Parent est toujours là


def test_object_component_stores_strings():
    w = make_world()
    a = w.create_entity()
    w.add_component(a, ("Label", "Jouer"))
    assert w.components["Label"][w.index_of(a)] == "Jouer"
    w.remove_component(a, "Label")
    assert w.components["Label"][w.index_of(a)] is None


def test_object_component_must_be_scalar_shape():
    w = make_world()
    try:
        w.register_component("Bad", object, (2,))
    except ValueError:
        return
    raise AssertionError("object + shape doit être refusé")


def test_duplicate_registration_is_refused():
    w = make_world()
    try:
        w.register_component("Pos", FLOAT32, (2,))
    except ValueError:
        return
    raise AssertionError("un nom déjà pris doit lever une erreur")


def test_64_components_max_and_last_bit_works():
    w = Registry(MAX_ENTITIES=4)
    for n in range(MAX_COMPONENTS):
        w.register_component(f"C{n}", FLOAT32)
    try:
        w.register_component("TooMany", FLOAT32)
        raise AssertionError("le 65e composant doit être refusé")
    except ValueError:
        pass
    # Le bit 63 est celui qui pose problème avec des int signés : on le vérifie.
    a = w.create_entity()
    w.add_component(a, ("C63", 1.0))
    assert w.query(w.get_mask("C63"))[0]
    w.remove_component(a, "C63")
    assert not w.query(w.get_mask("C63"))[0]


# ----------------------------------------------------------------------
# [EXERCICE] Les trois méthodes que tu écris
# ----------------------------------------------------------------------
def test_exercise_register_tag():
    w = make_world()
    w.register_tag("Node")
    assert "Node" not in w.components        # un tag n'a pas de tableau
    assert w.is_component_exist("Node")
    a = w.create_entity()
    w.add_component(a, "Node")               # ajout d'un tag : nom seul
    assert w.query(w.get_mask("Node"))[0]


def test_exercise_has_component():
    w = make_world()
    w.register_tag("Node")
    a = w.create_entity()
    w.add_component(a, ("Pos", (0, 0)), "Node")
    assert w.has_component(a, "Pos") is True
    assert w.has_component(a, "Node") is True
    assert w.has_component(a, "Parent") is False
    w.destroy_entity(a)
    assert w.has_component(a, "Pos") is False   # entité morte -> False, pas d'erreur


def test_exercise_get_component():
    w = make_world()
    a = w.create_entity()
    w.add_component(a, ("Pos", (3, 4)))
    pos = w.get_component(a, "Pos")
    assert tuple(pos) == (3, 4)
    pos[0] = 99                              # c'est une vue : ça écrit dans le tableau
    assert w.components["Pos"][w.index_of(a)][0] == 99
    try:
        w.get_component(a, "Parent")         # l'entité n'a pas ce composant
    except ValueError:
        return
    raise AssertionError("get_component doit lever ValueError si le composant manque")


# ----------------------------------------------------------------------
# Mini-lanceur (pas besoin de pytest)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  OK     {name}")
        except NotImplementedError as e:
            failed += 1
            print(f"  A FAIRE {name}  ->  {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ECHEC  {name}  ->  {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passent")
    raise SystemExit(1 if failed else 0)
