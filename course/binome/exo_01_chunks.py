"""
EXO 1 : un monde découpé en "chunks" (chez nous : des lignes)

Lancer :   python course/binome/exo_01_chunks.py
(aucune bibliothèque à installer, tout se passe dans le terminal)

======================================================================
LES CHUNKS EN DEUX MINUTES
======================================================================
Imagine un jeu avec un monde énorme et 1000 objets qui bougent.
À chaque image (60 fois par seconde), tu veux savoir si le joueur touche quelque chose.

Version naïve : tu compares le joueur avec les 1000 objets. Ça fait 60 000 tests par
seconde... alors que 990 de ces objets sont à des kilomètres du joueur. Du travail
complètement inutile.

L'idée : couper le monde en morceaux (les "chunks") et ranger chaque objet dans le sien.
Pour savoir si le joueur touche quelque chose, on regarde UNIQUEMENT le morceau où il se
trouve (et parfois ses voisins). Le reste du monde, on s'en fiche pour l'instant.

Minecraft fait exactement ça : le monde est coupé en colonnes de 16 x 16 blocs, et le jeu
ne charge et ne fait vivre que les chunks autour du joueur. Tu peux marcher des heures dans
un monde presque infini sans jamais t'en rendre compte, alors que le jeu ne travaille à
chaque instant que sur une toute petite partie.

Et chez nous ? Un véhicule ne peut gêner le joueur que s'il est SUR SA LIGNE. Donc :

    un chunk = une ligne

    monde   = une liste de lignes       (l'index dans la liste EST le numéro de ligne)
    ligne   = une liste d'éléments      (les choses qui bougent sur cette ligne)
    élément = un dictionnaire           (ses infos : nom, position, taille, vitesse)

Grâce à l'index, pour atteindre la ligne 3 on écrit simplement monde[3] : pas besoin de
chercher, on y va directement.

======================================================================
LES DONNÉES (déjà prêtes, ne les modifie pas)
======================================================================
Un élément occupe les cases  x, x+1, ..., x+longueur-1  de sa ligne.
Dans cet exo les données sont FIXES. Dans le vrai jeu, ces dictionnaires seraient mis à
jour sans arrêt (les véhicules avancent).
"""

monde = [
    [],  # ligne 0 : de l'herbe, rien ne bouge
    [    # ligne 1 : une route
        {"nom": "voiture", "x": 2, "longueur": 2, "vitesse": 3},
        {"nom": "camion",  "x": 7, "longueur": 4, "vitesse": 2},
    ],
    [    # ligne 2 : une route rapide
        {"nom": "moto", "x": 5, "longueur": 1, "vitesse": 6},
    ],
    [],  # ligne 3 : de l'herbe
    [    # ligne 4 : une route, sens inverse (vitesses négatives)
        {"nom": "voiture", "x": 10, "longueur": 2, "vitesse": -3},
        {"nom": "voiture", "x": 3,  "longueur": 2, "vitesse": -3},
        {"nom": "moto",    "x": 0,  "longueur": 1, "vitesse": -6},
    ],
]

joueur = {"colonne": 8, "ligne": 1}


# ======================================================================
# ÉTAPE 1 : se promener dans le monde
# ======================================================================
# Avec une boucle for (et même une boucle dans une boucle), affiche le contenu du monde,
# une ligne du monde par ligne d'écran, par exemple :
#
#       ligne 0 : (vide)
#       ligne 1 : voiture, camion
#       ...
#
# Piste : tu as besoin du numéro de la ligne ET de son contenu. Cherche ce que fait
# enumerate().
#
# >>> À TOI :


# ======================================================================
# ÉTAPE 2 : compter
# ======================================================================
# Affiche : le nombre total d'éléments dans le monde, le nombre d'éléments de chaque
# ligne, et le numéro de la ligne la plus remplie.
#
# Attendu : 6 éléments au total ; par ligne : 0, 2, 1, 0, 3 ; la plus remplie est la 4.
#
# >>> À TOI :


# ======================================================================
# ÉTAPE 3 : est-ce que le joueur touche un élément ?
# ======================================================================
# Le joueur est sur une COLONNE. Il touche un élément si sa colonne tombe dans les cases
# occupées par l'élément (de x jusqu'à x + longueur - 1 inclus).
#
# Écris les deux fonctions ci-dessous. Elles lisent les valeurs DANS les dictionnaires.
def touche(element: dict, colonne: int) -> bool:
    """ Vrai si l'élément occupe la case `colonne`. """
    # >>> À TOI : va chercher "x" et "longueur" dans le dictionnaire `element`.
    raise NotImplementedError("touche : à écrire")


def elements_touches(ligne: list, colonne: int) -> list:
    """ Renvoie la liste des NOMS des éléments de cette ligne qui touchent la colonne. """
    # >>> À TOI : une boucle for sur la ligne, et tu utilises touche().
    raise NotImplementedError("elements_touches : à écrire")


# ======================================================================
# ÉTAPE 4 : le test avec chunk, et le test sans chunk (on compte les efforts)
# ======================================================================
# Pour VOIR l'intérêt des chunks, on compte le nombre de tests que fait l'ordinateur.
#
# (a) SANS chunk : on oublie que le monde est rangé par lignes. Construis d'abord une
#     seule grande liste avec TOUS les éléments, en notant sur chacun sa ligne. Ensuite
#     parcours-la entièrement : pour chaque élément, il faut vérifier que c'est la bonne
#     ligne ET que la colonne touche. Compte combien d'éléments tu as dû examiner.
#
# (b) AVEC chunk : va directement à monde[joueur["ligne"]] et ne parcours que celle-là.
#     Compte combien d'éléments tu as examinés.
#
# Pour le joueur ci-dessus (colonne 8, ligne 1), attendu :
#       sans chunk : 6 éléments examinés      avec chunk : 2 éléments examinés
#       et dans les deux cas, il touche le camion.
#
# Ensuite, change la position du joueur (par exemple colonne 0, ligne 4) et recompare.
# Plus le monde est grand, plus l'écart explose. Pourquoi ?
#
# >>> À TOI :


# ======================================================================
# ÉTAPE 5 (bonus) : ça bouge !
# ======================================================================
# Dans le vrai jeu, les dictionnaires changent à chaque instant. Simulons ça.
# Écris `avancer(ligne)` : elle fait avancer chaque élément de la ligne d'autant de cases
# que sa vitesse (x devient x + vitesse). Elle MODIFIE les dictionnaires, elle ne renvoie rien.
def avancer(ligne: list) -> None:
    # >>> À TOI
    raise NotImplementedError("avancer : à écrire (bonus)")


# Puis, avec le joueur à la colonne 8 sur la ligne 1, répète 4 fois : afficher qui touche le
# joueur, puis avancer la ligne. Attendu :
#       tour 0 : camion      tour 1 : personne      tour 2 : voiture      tour 3 : personne
#
# Observe : le joueur n'a pas bougé, mais ce qui le touche change. Pourquoi ?
#
# >>> À TOI :


# ======================================================================
# ÉTAPE 6 : et maintenant, qu'est-ce qui te gêne ?
# ======================================================================
# Relis ton code et réponds à voix haute (ou en commentaire), avec tes mots :
#
#  - Si tu écris "longeur" au lieu de "longueur" quelque part, quand Python te prévient-il ?
#    Et si cette ligne ne s'exécute jamais dans ton test ?
#  - Chaque élément doit avoir les mêmes 4 clés. Qui te garantit qu'un élément n'en oublie pas une ?
#  - touche() et avancer() sont des fonctions séparées des données. Comment quelqu'un qui
#    lit ton code sait-il qu'elles vont avec ces dictionnaires ?
#  - Si chaque élément devait aussi avoir une couleur, une image, un son... que se passe-t-il
#    avec les dictionnaires ?
#
# La suite : ranger les données ET les fonctions qui vont avec ensemble, au même endroit.
# C'est exactement ce que fait une CLASSE. On y arrive à l'exo suivant.


# ======================================================================
# LA VÉRIFICATION AUTOMATIQUE (ne touche pas à ce qui suit)
# ======================================================================
def verifier() -> None:
    cas = [  # (colonne, ligne, noms attendus)
        (8, 1, ["camion"]),
        (5, 1, []),
        (5, 2, ["moto"]),
        (0, 4, ["moto"]),
        (10, 4, ["voiture"]),
        (1, 0, []),
    ]
    print("--- vérification de elements_touches (et touche)")
    try:
        for colonne, ligne, attendu in cas:
            obtenu = elements_touches(monde[ligne], colonne)
            etat = "OK     " if obtenu == attendu else "ECHEC  "
            print(f"  {etat} colonne {colonne}, ligne {ligne} : obtenu {obtenu}, attendu {attendu}")
    except NotImplementedError as e:
        print("  A FAIRE :", e)

    print("--- vérification de avancer (bonus)")
    try:
        import copy
        ligne = copy.deepcopy(monde[1])
        resultat = []
        for _ in range(4):
            resultat.append(elements_touches(ligne, 8))
            avancer(ligne)
        attendu = [["camion"], [], ["voiture"], []]
        print("  OK     " if resultat == attendu else f"  ECHEC   obtenu {resultat}, attendu {attendu}")
    except NotImplementedError as e:
        print("  A FAIRE :", e)


if __name__ == "__main__":
    verifier()
