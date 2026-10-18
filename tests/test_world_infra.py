"""
Tests de l'organisation de la frame : étages, commandes différées, ressources.

Lancer :   uv run tests/test_world_infra.py

Les tests marqués [EXERCICE] ne passent qu'une fois que tu as écrit :
  - Commands.remove_component   (ecam/core/commands.py)
  - Registry.add_stage          (ecam/core/registry.py)
  - Registry.get_resource       (ecam/core/registry.py)
  - Registry.remove_resource    (ecam/core/registry.py)
"""
from dataclasses import dataclass

from ecam.core.registry import Registry
from ecam.core.system import System
from ecam.core.types import FLOAT32


# Deux petites classes pour jouer le rôle de ressources
@dataclass
class Theme:
    name: str = "dark"


@dataclass
class ScreenSize:
    w: int = 1280
    h: int = 720


class Recorder(System):
    """ Un système qui note son nom dans une liste commune quand il s'exécute. """
    def __init__(self, registry, name, log):
        super().__init__(registry)
        self.name, self.log = name, log

    def update(self, dt):
        self.log.append(self.name)


class DespawnAll(System):
    """ Un système qui demande la destruction d'un groupe d'entités. """
    def __init__(self, registry, victims, log):
        super().__init__(registry)
        self.victims, self.log = victims, log

    def update(self, dt):
        for eid in self.victims:
            self.registry.commands.despawn(eid)
        # Les entités sont ENCORE vivantes ici : la destruction est différée.
        self.log.append(all(self.registry.is_alive(e) for e in self.victims))


class CheckAlive(System):
    """ Un système qui note si une entité est vivante au moment où il tourne. """
    def __init__(self, registry, eid, log):
        super().__init__(registry)
        self.eid, self.log = eid, log

    def update(self, dt):
        self.log.append(self.registry.is_alive(self.eid))


def make_world() -> Registry:
    w = Registry(MAX_ENTITIES=16)
    w.register_component("Pos", FLOAT32, (2,))
    w.register_tag("Node")
    return w


# ----------------------------------------------------------------------
# Étages
# ----------------------------------------------------------------------
def test_default_stages_run_in_order():
    w = make_world()
    log = []
    w.add_system(Recorder(w, "post", log), "post_update")
    w.add_system(Recorder(w, "input", log), "input")
    w.add_system(Recorder(w, "default", log))            # étage par défaut : "update"
    w.update_systems(0.016)
    assert log == ["input", "default", "post"]


def test_unknown_stage_is_refused():
    w = make_world()
    try:
        w.add_system(Recorder(w, "x", []), "nimporte_quoi")
    except ValueError:
        return
    raise AssertionError("un étage inconnu doit lever une erreur")


def test_get_system_searches_all_stages():
    w = make_world()
    rec = w.add_system(Recorder(w, "x", []), "post_update")
    assert w.get_system(Recorder) is rec


def test_disabled_system_is_skipped():
    w = make_world()
    log = []
    rec = w.add_system(Recorder(w, "x", log))
    rec.enabled = False
    w.update_systems(0.016)
    assert log == []


# ----------------------------------------------------------------------
# Commandes différées
# ----------------------------------------------------------------------
def test_despawn_is_deferred_until_stage_end():
    w = make_world()
    a, b = w.create_entity(), w.create_entity()
    log = []
    w.add_system(DespawnAll(w, [a, b], log))
    w.update_systems(0.016)
    assert log == [True]              # vivantes PENDANT le système...
    assert not w.is_alive(a)          # ...mortes une fois la frame passée
    assert not w.is_alive(b)
    assert w.count == 0


def test_despawn_applied_between_stages():
    # Une destruction demandée à l'étage "update" doit être visible dès l'étage suivant.
    w = make_world()
    a = w.create_entity()
    log = []
    w.add_system(DespawnAll(w, [a], []), "update")
    w.add_system(CheckAlive(w, a, log), "post_update")
    w.update_systems(0.016)
    assert log == [False]


def test_double_despawn_is_harmless():
    w = make_world()
    a = w.create_entity()
    w.commands.despawn(a)
    w.commands.despawn(a)
    w.commands.apply()                # pas d'erreur
    assert w.count == 0


def test_commands_queue_is_emptied_by_apply():
    w = make_world()
    w.commands.despawn(w.create_entity())
    assert len(w.commands) == 1
    w.commands.apply()
    assert len(w.commands) == 0


# ----------------------------------------------------------------------
# Ressources (insert_resource / has_resource sont déjà écrites)
# ----------------------------------------------------------------------
def test_insert_and_has_resource():
    w = make_world()
    assert not w.has_resource(Theme)
    theme = w.insert_resource(Theme("light"))
    assert w.has_resource(Theme)
    assert theme.name == "light"


def test_insert_replaces_same_type():
    w = make_world()
    w.insert_resource(Theme("dark"))
    w.insert_resource(Theme("light"))
    assert w.resources[Theme].name == "light"
    assert len(w.resources) == 1


# ----------------------------------------------------------------------
# [EXERCICE] Les quatre méthodes que tu écris
# ----------------------------------------------------------------------
def test_exercise_get_resource():
    w = make_world()
    theme = w.insert_resource(Theme())
    assert w.get_resource(Theme) is theme       # le MÊME objet, pas une copie
    try:
        w.get_resource(ScreenSize)
    except KeyError as e:
        assert "ScreenSize" in str(e)           # le message nomme le type manquant
        return
    raise AssertionError("get_resource doit lever KeyError si la ressource manque")


def test_exercise_remove_resource():
    w = make_world()
    theme = w.insert_resource(Theme())
    assert w.remove_resource(Theme) is theme
    assert not w.has_resource(Theme)
    assert w.remove_resource(Theme) is None     # déjà retirée : pas d'erreur


def test_exercise_remove_component_command():
    w = make_world()
    a = w.create_entity()
    w.add_component(a, ("Pos", (1, 2)), "Node")
    w.commands.remove_component(a, "Node")
    assert w.has_component(a, "Node")           # pas encore : c'est différé
    w.commands.apply()
    assert not w.has_component(a, "Node")
    assert w.has_component(a, "Pos")            # le reste n'a pas bougé


def test_exercise_remove_component_command_on_destroyed_entity():
    # L'entité meurt AVANT que la commande de retrait ne s'exécute : pas d'erreur.
    w = make_world()
    a = w.create_entity()
    w.add_component(a, "Node")
    w.commands.despawn(a)
    w.commands.remove_component(a, "Node")
    w.commands.apply()
    assert not w.is_alive(a)


def test_exercise_add_stage_after_and_before():
    w = make_world()
    w.add_stage("layout", after="update")
    w.add_stage("early", before="input")
    w.add_stage("last")
    assert w.stages == ["early", "input", "update", "layout", "post_update", "last"]


def test_exercise_add_stage_runs_systems_in_new_order():
    w = make_world()
    w.add_stage("layout", after="update")
    log = []
    w.add_system(Recorder(w, "post", log), "post_update")
    w.add_system(Recorder(w, "layout", log), "layout")
    w.add_system(Recorder(w, "update", log), "update")
    w.update_systems(0.016)
    assert log == ["update", "layout", "post"]


def test_exercise_add_stage_errors():
    w = make_world()
    for bad_call in (
        lambda: w.add_stage("update"),                                # nom déjà pris
        lambda: w.add_stage("x", after="update", before="input"),     # les deux à la fois
        lambda: w.add_stage("x", after="inconnu"),                    # référence inconnue
    ):
        try:
            bad_call()
        except ValueError:
            continue
        raise AssertionError("cet appel aurait dû lever ValueError")


# ----------------------------------------------------------------------
# Mini-lanceur (pas besoin de pytest)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  OK      {name}")
        except NotImplementedError as e:
            failed += 1
            print(f"  A FAIRE {name}  ->  {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ECHEC   {name}  ->  {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passent")
    raise SystemExit(1 if failed else 0)
