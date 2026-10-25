"""
LEÇON 2 : de la classe aux données + fonctions

Lancer :   uv run course/lecon_02_classe_vers_donnees.py
(numpy n'est même pas nécessaire ici : c'est du Python pur)

CONTEXTE
--------
Une classe, c'est deux choses collées ensemble : des DONNÉES (les attributs) et des
FONCTIONS qui les manipulent (les méthodes). L'état est caché dans `self`.

En programmation orientée données, on les sépare :

        classe :    ball.move(dt)                     <- l'état est dans `ball`, caché
        données :   move_ball(ball, dt)               <- l'état est visible, passé en argument

C'est le même comportement. Ce qui change, c'est QUI sait QUOI :
  - les données sont déclarées à UN endroit, sans aucune logique ;
  - les fonctions sont des verbes, classés par sujet ("physique", "briques"...) et non
    par type ;
  - chaque fonction annonce dans sa SIGNATURE ce dont elle a besoin. On ne passe que le
    strict nécessaire : `bounce_walls(ball, width)` n'a pas besoin de connaître les briques.

Ce que tu vas faire : on te donne un mini casse-briques écrit AVEC des classes (partie A).
Tu l'écris de nouveau SANS méthode (partie B), puis un banc d'essai vérifie que les deux
versions se comportent EXACTEMENT pareil, image par image (partie C).

Règle de la leçon : `class` n'est autorisé que pour déclarer des champs. Aucune méthode.
"""
from dataclasses import dataclass, field

DT = 0.1
STEPS = 170

# Quatre départs différents de la balle (x, y, vx, vy). Chacun fait vivre des choses
# différentes : murs, raquette, briques, perte de la balle à des moments variés.
SCENARIOS = [
    (30.0, 40.0, 23.0, -31.0),
    (45.0, 40.0, 17.0, -31.0),
    (5.0, 30.0, -21.0, -33.0),
    (62.0, 40.0, 23.0, -41.0),
]


# ======================================================================
# PARTIE A : la version avec des classes (ÉCRITE POUR TOI : à LIRE attentivement)
# ======================================================================
# Lis-la comme une enquête : tu dois en extraire toutes les DONNÉES (quelles valeurs de
# départ ? quelles tailles ?) et tous les COMPORTEMENTS, ainsi que l'ORDRE dans lequel
# ils s'enchaînent. Garde le même ordre dans ta version : c'est plus simple à comparer.
class Brick:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.alive = True

    def contains(self, px, py):
        return self.alive and self.x <= px < self.x + self.w and self.y <= py < self.y + self.h


class Paddle:
    def __init__(self, x, y, w):
        self.x, self.y, self.w = x, y, w

    def covers(self, px):
        return self.x - self.w / 2 <= px <= self.x + self.w / 2


class Ball:
    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

    def move(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def bounce_walls(self, width):
        # murs gauche/droit : on renvoie la balle de l'autre côté du mur (symétrie)
        if self.x < 0:
            self.x = -self.x
            self.vx = -self.vx
        elif self.x > width:
            self.x = 2 * width - self.x
            self.vx = -self.vx
        # plafond
        if self.y < 0:
            self.y = -self.y
            self.vy = -self.vy

    def bounce_paddle(self, paddle):
        # seulement si la balle descend, a atteint la raquette et est au-dessus d'elle
        if self.vy > 0 and self.y >= paddle.y and paddle.covers(self.x):
            self.y = 2 * paddle.y - self.y
            self.vy = -self.vy


class Game:
    def __init__(self, ball_start=(30.0, 40.0, 23.0, -31.0)):
        self.width, self.height = 100, 60
        self.ball = Ball(*ball_start)
        self.paddle = Paddle(50.0, 55.0, 50.0)
        self.bricks = [Brick(10 + 16 * i, 8 + 8 * j, 14, 6) for i in range(5) for j in range(2)]
        self.score = 0
        self.lost = False

    def hit_bricks(self):
        for brick in self.bricks:
            if brick.contains(self.ball.x, self.ball.y):
                brick.alive = False
                self.ball.vy = -self.ball.vy
                self.score += 10
                break  # on s'arrête à la première brique trouvée

    def update(self, dt):
        if self.lost:
            return
        self.ball.move(dt)
        self.ball.bounce_walls(self.width)
        self.ball.bounce_paddle(self.paddle)
        self.hit_bricks()
        if self.ball.y > self.height:
            self.lost = True


# ======================================================================
# PARTIE B : la version SANS méthode (À TOI DE JOUER)
# ======================================================================
# B1. Les DONNÉES : déclarées pour toi (juste des champs, aucune méthode).
@dataclass(slots=True)
class BallData:
    x: float
    y: float
    vx: float
    vy: float


@dataclass(slots=True)
class PaddleData:
    x: float
    y: float
    w: float


@dataclass(slots=True)
class BrickData:
    x: float
    y: float
    w: float
    h: float
    alive: bool = True


@dataclass(slots=True)
class World:
    ball: BallData
    paddle: PaddleData
    bricks: list[BrickData]
    width: float
    height: float
    score: int = 0
    lost: bool = False


# B2. Une fonction écrite pour toi : LE MODÈLE à imiter.
#     Compare-la avec Ball.move : `self` est devenu un premier argument explicite.
def move_ball(ball: BallData, dt: float) -> None:
    ball.x += ball.vx * dt
    ball.y += ball.vy * dt


# B3. À toi : les cinq autres. Garde les noms et les signatures, ils sont attendus par le banc d'essai.
def make_world(ball_start: tuple = (30.0, 40.0, 23.0, -31.0)) -> World:
    """ Construit l'état de départ : le MÊME que Game.__init__. """
    # >>> À TOI DE JOUER (1/5)
    # Relis Game.__init__ : quelles valeurs de départ pour la balle, la raquette, les briques,
    # la taille du monde ? Pour les briques, une boucle ou une compréhension de liste,
    # dans le même ordre que dans la version avec classes.
    # La balle part de la position `ball_start` = (x, y, vx, vy) reçue en argument.
    raise NotImplementedError("make_world : à écrire")


def bounce_walls(ball: BallData, width: float) -> None:
    """ Équivalent de Ball.bounce_walls. """
    # >>> À TOI DE JOUER (2/5)
    # On ne passe QUE ce dont on a besoin : la balle et la largeur du monde.
    raise NotImplementedError("bounce_walls : à écrire")


def bounce_paddle(ball: BallData, paddle: PaddleData) -> None:
    """ Équivalent de Ball.bounce_paddle (et de Paddle.covers). """
    # >>> À TOI DE JOUER (3/5)
    # Paddle.covers était une méthode : ici il n'y a plus de méthode. Tu peux écrire le test
    # directement dans la fonction, ou faire une petite fonction à part (ton choix : justifie-le
    # dans la question Q2).
    raise NotImplementedError("bounce_paddle : à écrire")


def hit_bricks(world: World) -> None:
    """ Équivalent de Game.hit_bricks. """
    # >>> À TOI DE JOUER (4/5)
    # Cette fonction a besoin de plusieurs choses (la balle, les briques ET le score) : ici on
    # lui donne tout le `world`. Pourquoi pas seulement la balle ? C'est la question Q3.
    raise NotImplementedError("hit_bricks : à écrire")


def update(world: World, dt: float) -> None:
    """ Équivalent de Game.update : enchaîne les étapes, DANS LE MÊME ORDRE. """
    # >>> À TOI DE JOUER (5/5)
    # N'oublie pas le cas "partie perdue" au début, et la détection de la perte à la fin.
    raise NotImplementedError("update : à écrire")


# ======================================================================
# PARTIE C : LE BANC D'ESSAI (écrit pour toi)
# ======================================================================
# Pour comparer, on prend une "photo" de l'état après chaque image, sous la même forme.
def snapshot_oop(g: Game) -> tuple:
    return (round(g.ball.x, 6), round(g.ball.y, 6), round(g.ball.vx, 6), round(g.ball.vy, 6),
            g.score, sum(b.alive for b in g.bricks), g.lost)


def snapshot_pod(w: World) -> tuple:
    return (round(w.ball.x, 6), round(w.ball.y, 6), round(w.ball.vx, 6), round(w.ball.vy, 6),
            w.score, sum(b.alive for b in w.bricks), w.lost)


def run_oop(ball_start: tuple) -> list[tuple]:
    game = Game(ball_start)
    photos = []
    for _ in range(STEPS):
        game.update(DT)
        photos.append(snapshot_oop(game))
    return photos


def run_pod(ball_start: tuple) -> list[tuple]:
    world = make_world(ball_start)
    photos = []
    for _ in range(STEPS):
        update(world, DT)
        photos.append(snapshot_pod(world))
    return photos


def main() -> None:
    print("=== Version avec classes (référence)")
    for depart in SCENARIOS:
        score, restantes, perdu = run_oop(depart)[-1][4:]
        print(f"  départ {depart} : score {score}, {restantes} briques restantes, perdue : {perdu}")

    print("\n=== Ta version sans méthode")
    tout_ok = True
    for depart in SCENARIOS:
        attendu = run_oop(depart)
        try:
            obtenu = run_pod(depart)
        except NotImplementedError as e:
            print("  A FAIRE :", e)
            return
        difference = next((n for n, (a, b) in enumerate(zip(attendu, obtenu)) if a != b), None)
        if difference is None:
            print(f"  OK     départ {depart}")
        else:
            tout_ok = False
            print(f"  ECHEC  départ {depart} : première différence à l'image {difference}")
            print(f"           classes : {attendu[difference]}")
            print(f"           tienne  : {obtenu[difference]}")
            print("           (format : x, y, vx, vy, score, briques restantes, perdu)")
    if tout_ok:
        print(f"\n  Bravo : les {STEPS} images sont IDENTIQUES sur les {len(SCENARIOS)} départs.")


if __name__ == "__main__":
    main()


# ======================================================================
# PARTIE D (bonus) : des briques spéciales, SANS héritage
# ======================================================================
# Avec des classes, on aurait pensé : "BriqueDure(Brick)" et "BriqueBonus(Brick)".
# Sans héritage : une brique est une donnée. Ajoute à BrickData ce qu'il faut pour que :
#   - une brique "dure" résiste à 2 coups,
#   - une brique "bonus" rapporte 50 points au lieu de 10.
# Pas de nouvelle classe, pas de nouvelle méthode. Réfléchis d'abord : quel champ ajouter ?
# Où mettre les points de chaque type (un dictionnaire de correspondance ?) ?
# Et si demain tu as vingt types de briques, qu'est-ce qui reste simple, qu'est-ce qui devient lourd ?


# ======================================================================
# QUESTIONS DE RÉFLEXION : réponds ici, en commentaire, avec tes mots
# ======================================================================
# Q1. Pour écrire make_world, qu'as-tu dû aller LIRE dans la version avec classes ?
#     (valeurs cachées dans __init__, ordre des briques...) Que cela dit-il sur la
#     visibilité de l'état dans une classe, comparé à ta version ?
#
# Q2. bounce_paddle(ball, paddle) contre Ball.bounce_paddle(self, paddle) : quand
#     tu lis un appel dans update(), que sais-tu des DONNÉES touchées dans chaque cas ?
#     Qu'as-tu décidé pour "covers" (dans la fonction, ou à part) et pourquoi ?
#
# Q3. hit_bricks reçoit tout le `world`, alors que bounce_walls ne reçoit que la balle et
#     la largeur. Quelle règle t'a guidé pour choisir ? Que perd-on à tout passer partout ?
#
# Q4. Où est passé `self` ? Dans la version sans méthode, quelles lignes de update()
#     montrent clairement quelles données chaque étape modifie ?
#
# Q5. Qu'as-tu gagné, qu'as-tu perdu ? Cite un cas où la classe te semble MEILLEURE.
#
# Q6. (une expérience) Dans update(), inverse l'ordre des étapes : teste les briques
#     AVANT les rebonds sur les murs et la raquette. Le banc d'essai le remarque-t-il ?
#     Surprise ? Réfléchis à la géométrie de CE jeu : pourquoi l'ordre ne change-t-il rien ici ?
#     Dans quel autre jeu l'ordre changerait-il le résultat ? Qu'en conclus-tu sur ce que
#     prouve un test qui dit OK ?
