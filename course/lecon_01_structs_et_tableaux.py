"""
LEÇON 1 : struct et tableaux  (AoS contre SoA), et on MESURE.

Lancer :   uv run course/lecon_01_structs_et_tableaux.py
(ce fichier n'utilise que numpy : il ne dépend pas d'ECAM)

CONTEXTE
--------
On veut faire avancer N particules : chacune a une position (x, y) et une
vitesse (vx, vy). Le calcul est toujours le même :

        x += vx * dt        y += vy * dt

On va stocker ces N particules de TROIS façons et comparer :

  1. AoS  (Array of Structs)   : une liste de petites structures.
                                 C'est la façon "naturelle" quand on vient de l'objet.
  2. SoA  (Struct of Arrays)   : une structure qui contient UN tableau par champ.
                                 C'est ce que fait ton Registry.
  3. Tableau structuré numpy   : un seul tableau dont chaque case est un
                                 "enregistrement" (x, y, vx, vy). C'est la
                                 struct C la plus fidèle qu'on puisse avoir en Python.

Ton travail : écrire les parties 2 et 3 (4 petites fonctions). La partie 1 est
écrite en entier : elle te montre le modèle à suivre.
"""
from dataclasses import dataclass
from time import perf_counter

import numpy as np

N_SMALL = 1_000
N_BIG = 200_000
DT = 0.016
STEPS = 10  # nombre de pas de simulation dans chaque mesure


# ----------------------------------------------------------------------
# VOS PRÉDICTIONS : écris-les ICI, AVANT de lancer le programme.
# (c'est le point le plus important de la leçon : se tromper est utile)
#
#   Pour N = 200 000, je pense que :
#     - SoA va être  ___ fois plus rapide / lent que AoS parce que ...
#     - le tableau structuré va être ...
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# DONNÉES DE DÉPART COMMUNES
# Les trois versions partent exactement des mêmes valeurs : c'est ce qui
# nous permet de vérifier qu'elles calculent la même chose.
# ----------------------------------------------------------------------
def initial_state(n: int):
    """ Renvoie quatre tableaux numpy float32 de taille n : x, y, vx, vy. """
    rng = np.random.default_rng(42)
    x = rng.uniform(0, 1280, n).astype(np.float32)
    y = rng.uniform(0, 720, n).astype(np.float32)
    vx = rng.uniform(-100, 100, n).astype(np.float32)
    vy = rng.uniform(-100, 100, n).astype(np.float32)
    return x, y, vx, vy


# ======================================================================
# PARTIE 1 : AoS, une liste de structures   (ÉCRIT POUR TOI : le modèle)
# ======================================================================
@dataclass(slots=True)
class Particle:
    # Le mot "class" n'est ici qu'une DÉCLARATION DE CHAMPS : c'est notre struct.
    # Règles du cours : aucune méthode, aucun héritage.
    # `slots=True` supprime le dictionnaire interne de chaque objet : moins de
    # mémoire, accès plus rapide (explication en commentaire de fin de fichier).
    x: float
    y: float
    vx: float
    vy: float


def make_aos(n: int) -> list[Particle]:
    """ Construit la liste de n particules. """
    x, y, vx, vy = initial_state(n)
    # .tolist() convertit en vrais float Python (valeurs identiques)
    return [Particle(*champs) for champs in zip(x.tolist(), y.tolist(), vx.tolist(), vy.tolist())]


def step_aos(particles: list[Particle], dt: float) -> None:
    """ Fait avancer toutes les particules, UNE PAR UNE. """
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt


# ======================================================================
# PARTIE 2 : SoA, un tableau par champ     (À TOI DE JOUER 1/2)
# ======================================================================
# CONTRAT : la structure est un simple dict {"x": tableau, "y": ..., "vx": ..., "vy": ...}
# Pas de classe : un dict est notre "struct de tableaux".
def make_soa(n: int) -> dict[str, np.ndarray]:
    """ Construit le dict de 4 tableaux numpy (float32, taille n). """
    # --- À TOI DE JOUER --------------------------------------------------
    # 1. Récupère les 4 tableaux avec initial_state(n).
    # 2. Renvoie-les dans un dict avec les clés "x", "y", "vx", "vy".
    raise NotImplementedError("make_soa : à implémenter")


def step_soa(p: dict[str, np.ndarray], dt: float) -> None:
    """ Fait avancer TOUTES les particules en deux lignes, sans boucle Python. """
    # --- À TOI DE JOUER --------------------------------------------------
    # Compare avec step_aos : il n'y a plus de `for`. Une opération numpy agit
    # sur tout le tableau d'un coup. Attention : il faut MODIFIER les tableaux
    # en place (opérateur +=), pas en créer de nouveaux, sinon l'appelant ne
    # verrait rien changer.
    raise NotImplementedError("step_soa : à implémenter")


# ======================================================================
# PARTIE 3 : tableau structuré numpy        (À TOI DE JOUER 2/2)
# ======================================================================
# CONTRAT : un seul np.ndarray dont les cases ont les champs "x", "y", "vx", "vy"
def make_structured(n: int) -> np.ndarray:
    """ Construit UN tableau de n enregistrements (x, y, vx, vy) en float32. """
    # --- À TOI DE JOUER --------------------------------------------------
    # 1. Décris la struct :
    #       dtype = np.dtype([("x", np.float32), ("y", np.float32), ...])
    #    (c'est littéralement la déclaration d'une struct C)
    # 2. Crée le tableau :  np.empty(n, dtype=dtype)
    # 3. Remplis chaque champ : tableau["x"] = ...   (avec initial_state)
    raise NotImplementedError("make_structured : à implémenter")


def step_structured(records: np.ndarray, dt: float) -> None:
    """ Même calcul, sur le tableau d'enregistrements. """
    # --- À TOI DE JOUER --------------------------------------------------
    # records["x"] donne une VUE sur le champ x de tous les enregistrements.
    # Le calcul ressemble beaucoup à step_soa.
    raise NotImplementedError("step_structured : à implémenter")


# ======================================================================
# LE BANC D'ESSAI (écrit pour toi)
# ======================================================================
def positions_aos(particles):
    return np.array([(p.x, p.y) for p in particles], dtype=np.float32)


def positions_soa(p):
    return np.stack([p["x"], p["y"]], axis=1)


def positions_structured(records):
    return np.stack([records["x"], records["y"]], axis=1)


# Pour chaque version : (nom, fabrique, pas de simulation, extracteur de positions)
VERSIONS = [
    ("AoS (liste)",       make_aos,        step_aos,        positions_aos),
    ("SoA (dict)",        make_soa,        step_soa,        positions_soa),
    ("Struct numpy",      make_structured, step_structured, positions_structured),
]


def best_time(make, step, n: int, repeats: int = 3) -> float:
    """ Meilleur temps (en ms) pour STEPS pas de simulation. Le minimum limite le bruit. """
    data = make(n)
    essais = []
    for _ in range(repeats):
        debut = perf_counter()
        for _ in range(STEPS):
            step(data, DT)
        essais.append(perf_counter() - debut)
    return min(essais) * 1000


def check_same_result(n: int = 500) -> dict[str, bool]:
    """ Les trois versions doivent calculer les mêmes positions (à float32 près). """
    # On prend AoS comme référence : sa partie est écrite pour toi.
    reference = make_aos(n)
    for _ in range(STEPS):
        step_aos(reference, DT)
    attendu = positions_aos(reference)

    resultats = {}
    for nom, make, step, positions in VERSIONS[1:]:
        try:
            data = make(n)
            for _ in range(STEPS):
                step(data, DT)
            resultats[nom] = bool(np.allclose(positions(data), attendu, atol=1e-2))
        except NotImplementedError:
            resultats[nom] = None  # pas encore écrite
    return resultats


def main() -> None:
    print("=== 1. CORRECTION : les trois versions calculent-elles pareil ?")
    for nom, ok in check_same_result().items():
        etat = "A FAIRE" if ok is None else ("OK" if ok else "ECHEC (résultat différent)")
        print(f"  {etat:<28} {nom}")

    print("\n=== 2. VITESSE : meilleur temps pour", STEPS, "pas (en ms, plus petit = mieux)")
    print(f"  {'':<14}" + "".join(f"{n:>14,}" for n in (N_SMALL, N_BIG)))
    temps = {}
    for nom, make, step, _ in VERSIONS:
        ligne = []
        for n in (N_SMALL, N_BIG):
            try:
                ligne.append(best_time(make, step, n))
            except NotImplementedError:
                ligne.append(None)
        temps[nom] = ligne
        print(f"  {nom:<14}" + "".join(f"{'à faire':>14}" if t is None else f"{t:>14.2f}" for t in ligne))

    base = temps["AoS (liste)"]
    print("\n=== 3. ACCÉLÉRATION par rapport à AoS")
    for nom, ligne in temps.items():
        if nom == "AoS (liste)" or None in ligne:
            continue
        rapports = [f"x{base[i] / ligne[i]:.0f}" for i in range(2)]
        print(f"  {nom:<14}" + "".join(f"{r:>14}" for r in rapports))

    print("\nRelis ta prédiction. Où t'es-tu trompé ? Réponds aux questions ci-dessous.")


if __name__ == "__main__":
    main()


# ======================================================================
# QUESTIONS DE RÉFLEXION : réponds ici, en commentaire, avec tes mots
# ======================================================================
# Q1. Pourquoi le résultat pour N = 1 000 est-il bien moins spectaculaire que
#     pour N = 200 000 ? (indice : combien coûte UN appel à numpy, même
#     pour un tableau minuscule ?)
#
# Q2. step_aos fait la MÊME chose que step_soa, mais est bien plus lent.
#     Qui exécute la boucle dans chaque cas : Python ou du code C ?
#
# Q3. Le tableau structuré range les 4 champs d'une particule côte à côte en
#     mémoire (x,y,vx,vy,x,y,vx,vy,...) alors que le SoA range tous les x
#     ensemble. Pour le calcul `x += vx*dt`, laquelle de ces deux dispositions
#     te semble la plus favorable, et pourquoi ? Le résultat mesuré confirme-t-il ?
#
# Q4. Dans ton Registry, "Transform" a la forme (N, 2) : un tableau par
#     composant. Est-ce plutôt du SoA ou de l'AoS ? Et à l'intérieur de
#     Transform (x et y d'une même entité côte à côte) ?
#
# ----------------------------------------------------------------------
# ANNEXE : pourquoi `slots=True` ?
# Un objet Python ordinaire garde ses attributs dans un dictionnaire caché
# (self.__dict__). `slots=True` remplace ce dictionnaire par des cases fixes :
# l'objet est plus petit et ses attributs plus rapides à lire. C'est le plus
# proche d'une vraie struct qu'on puisse obtenir avec un objet Python, mais
# attention : chaque particule reste un objet séparé, quelque part en mémoire,
# alors que dans un tableau numpy toutes les valeurs sont collées.
# ----------------------------------------------------------------------
