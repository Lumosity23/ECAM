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

N_SMALL = 10_000
N_BIG = 2_000_000
DT = 0.016
STEPS = 10  # nombre de pas de simulation dans chaque mesure


# ----------------------------------------------------------------------
# VOS PRÉDICTIONS : écris-les ICI, AVANT de lancer le programme.
# (c'est le point le plus important de la leçon : se tromper est utile)
#
#   Pour N = 200 000, je pense que :
#     - SoA va être  100 fois plus rapide que AoS parce que : pour realiser une boucle d'operation sur un tyhpe de donne
#       si on a directmeent le tableua de donne de tout le monde ca fit directement dans le cache du processeur alors que
#       si on a des structure on va devoir pourchacun aller cherche l'info qu'il nous faut et donc ne pas pouvoir tout mettre dans
#       le cache du process et donc faire plusieur appel memoire et donc perdre bcp de temps
#     - le tableau structuré va être bcp plus lent du au raison ennoecer plus haut
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# DONNÉES DE DÉPART COMMUNES
# Les trois versions partent exactement des mêmes valeurs : c'est ce qui
# nous permet de vérifier qu'elles calculent la même chose.
# ----------------------------------------------------------------------
def initial_state(n: int):
    """Renvoie quatre tableaux numpy float32 de taille n : x, y, vx, vy."""
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
    """Construit la liste de n particules."""
    x, y, vx, vy = initial_state(n)
    # .tolist() convertit en vrais float Python (valeurs identiques)
    return [
        Particle(*champs)
        for champs in zip(x.tolist(), y.tolist(), vx.tolist(), vy.tolist())
    ]


def step_aos(particles: list[Particle], dt: float) -> None:
    """Fait avancer toutes les particules, UNE PAR UNE."""
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt


# ======================================================================
# PARTIE 2 : SoA, un tableau par champ
# ======================================================================
def make_soa(n: int) -> dict[str, np.ndarray]:
    """Construit le dict de 4 tableaux numpy (float32, taille n)."""
    return dict(zip(["x", "y", "vx", "vy"], initial_state(n)))


def step_soa(p: dict[str, np.ndarray], dt: float) -> None:
    """Fait avancer TOUTES les particules en deux lignes, sans boucle Python."""
    p["x"] += p["vx"] * dt
    p["y"] += p["vy"] * dt


# ======================================================================
# PARTIE 3 : tableau structuré numpy        (À TOI DE JOUER 2/2)
# ======================================================================
def make_structured(n: int) -> np.ndarray:
    """Construit UN tableau de n enregistrements (x, y, vx, vy) en float32."""
    dtype = np.dtype(
        [("x", np.float32), ("y", np.float32), ("vx", np.float32), ("vy", np.float32)]
    )
    tableau = np.empty(n, dtype=dtype)
    x, y, vx, vy = initial_state(n)
    tableau["x"] = x
    tableau["y"] = y
    tableau["vx"] = vx
    tableau["vy"] = vy

    return tableau


def step_structured(records: np.ndarray, dt: float) -> None:
    """Même calcul, sur le tableau d'enregistrements."""
    records["x"] += records["vx"] * dt
    records["y"] += records["vy"] * dt


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
    ("AoS (liste)", make_aos, step_aos, positions_aos),
    ("SoA (dict)", make_soa, step_soa, positions_soa),
    ("Struct numpy", make_structured, step_structured, positions_structured),
]


def best_time(make, step, n: int, repeats: int = 3) -> float:
    """Meilleur temps (en ms) pour STEPS pas de simulation. Le minimum limite le bruit."""
    data = make(n)
    essais = []
    for _ in range(repeats):
        debut = perf_counter()
        for _ in range(STEPS):
            step(data, DT)
        essais.append(perf_counter() - debut)
    return min(essais) * 1000


def check_same_result(n: int = 500) -> dict[str, bool]:
    """Les trois versions doivent calculer les mêmes positions (à float32 près)."""
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
        etat = (
            "A FAIRE" if ok is None else ("OK" if ok else "ECHEC (résultat différent)")
        )
        print(f"  {etat:<28} {nom}")

    print(
        "\n=== 2. VITESSE : meilleur temps pour",
        STEPS,
        "pas (en ms, plus petit = mieux)",
    )
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
        print(
            f"  {nom:<14}"
            + "".join(f"{'à faire':>14}" if t is None else f"{t:>14.2f}" for t in ligne)
        )

    base = temps["AoS (liste)"]
    print("\n=== 3. ACCÉLÉRATION par rapport à AoS")
    for nom, ligne in temps.items():
        if nom == "AoS (liste)" or None in ligne:
            continue
        rapports = [f"x{base[i] / ligne[i]:.0f}" for i in range(2)]
        print(f"  {nom:<14}" + "".join(f"{r:>14}" for r in rapports))

    print(
        "\nRelis ta prédiction. Où t'es-tu trompé ? Réponds aux questions ci-dessous."
    )


if __name__ == "__main__":
    main()


# ======================================================================
# QUESTIONS DE RÉFLEXION : réponds ici, en commentaire, avec tes mots
# ======================================================================
# Q1. Pourquoi le résultat pour N = 1 000 est-il bien moins spectaculaire que
#     pour N = 200 000 ? (indice : combien coûte UN appel à numpy, même
#     pour un tableau minuscule ?)
#
#       comme la quantite de particule est enore negligablea le plus grand temps passer est celui des appel et non
#       celui du calcul pure et donc pour 200_000 entites la le calcule prime
#
# Q2. step_aos fait la MÊME chose que step_soa, mais est bien plus lent.
#     Qui exécute la boucle dans chaque cas : Python ou du code C ?
#
#       dans l'un on a fais un .tolist() qui fais perder tout les performance de numpy et on retombe sur une boucle for
#       classique python -> aos ( on a une liste de struture python )
#       et pout SOA -> on a un dico python qui contient de array de numpy donc tout les operation sont faitre cote numpy et
#       cote python on reste toujours super rapide avec notre O(1) grace au dico
#
# Q3. Le tableau structuré range les 4 champs d'une particule côte à côte en
#     mémoire (x,y,vx,vy,x,y,vx,vy,...) alors que le SoA range tous les x
#     ensemble. Pour le calcul `x += vx*dt`, laquelle de ces deux dispositions
#     te semble la plus favorable, et pourquoi ? Le résultat mesuré confirme-t-il ?
#
#       car comme ca on peux lire tout les valuer d'une meme propriete en meme temps et donc pour un calcul simple
#       'x += vx * dt' on n'as qu'as load en cache l'array 'x' et 'vx' et c'est tout alors que pour l'autre on va devoir laod chacune
#       des struct pour aller cherche les valuer de x et vx donc bcp plus d'appel memoire pour le meme travaille ( et le procs il n'aime pas les appel memoire )
#
#
# Q4. Dans ton Registry, "Transform" a la forme (N, 2) : un tableau par
#     composant. Est-ce plutôt du SoA ou de l'AoS ? Et à l'intérieur de
#     Transform (x et y d'une même entité côte à côte) ?
#
#       je dirai que c'est une SoA car on a notre struct "Transform" qui contient deux tableau chacun pour une valeur : 'x' et 'y'
#       et donc non elle ne sont pas cote a cote mais on le meme index ( dense ) pour que on puisse avec une seul ID retrouver tout ce qu'on veux
#       d'une entity ( le but d'un ECS )
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
