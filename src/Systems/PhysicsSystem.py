import itertools
import math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from registry import Registry


def PhysicsSystem(ecs: "Registry", delta_time: float, screen_size: tuple[int, int], rayon: int) -> None:
    MASK_PHYSIC = ecs.GetMask("Transform")
    w, h = screen_size

    is_valid, transform, velocity = ecs.View(MASK_PHYSIC, "Transform", "Velocity")

    # velocity[is_valid, 1] += 981 * delta_time

    transform[is_valid] += velocity[is_valid] * delta_time

    x = transform[:, 0]
    y = transform[:, 1]

    vel_x = velocity[:, 0]
    vel_y = velocity[:, 1]

    hit_bottom = (y >= h - rayon) & is_valid
    y[hit_bottom] = h - rayon
    vel_y[hit_bottom] *= -0.7
    
    hit_top = (y <= rayon) & is_valid
    y[hit_top] = rayon
    vel_y[hit_top] *= -0.7

    hit_right = (x >= w - rayon) & is_valid
    x[hit_right] = w - rayon
    vel_x[hit_right] *= -0.7

    hit_left = (x <= rayon) & is_valid
    x[hit_left] = rayon
    vel_x[hit_left] *= -0.7


def CollisionSystem(ecs: "Registry", rayon_entite: float) -> None:
    # 1. On récupère directement les tableaux complets (plus rapide pour un accès par index aléatoire)
    # Attention, on suppose que tes composants s'appellent "Transform" et "Velocity" !
    transform = ecs.components.get("Transform")
    velocity = ecs.components.get("Velocity")
    paires_verifiees = set()

    if transform is None or velocity is None: raise ValueError("Transform et/ou Velocity n'existe pas !")

    # 2. On boucle UNIQUEMENT sur les chunks de notre grille spatiale
    for (cx, cy), entites_locales in ecs.spatial_grid.items():    
        for id1 in entites_locales:
            # Renvoie les chunks autour du chunk en question avec un rayon de 1 ( donc 9 cases )
            for chunk in ecs.GetEntitiesAround(cx, cy, 1):
                for id2 in chunk:
                    if id1 == id2:
                        continue
                    
                    paire = tuple(sorted((id1, id2)))
                    if paire in paires_verifiees:
                        continue

                    paires_verifiees.add(paire)
            
                    x1, y1 = transform[id1]
                    x2, y2 = transform[id2]

                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx**2 + dy**2)

                    # ÉTAPE C : La condition de collision
                    # Si la distance est plus petite que (rayon_entite * 2) :
                    min_distance = rayon_entite * 2

                    # (On ajoute distance > 0.0001 pour éviter de diviser par zéro si elles sont exactement au même pixel !)
                    if 0.0001 < distance < min_distance:

                        # 1. CALCUL DE L'ENCASTREMENT (Combien de pixels sont coincés ?)
                        overlap = min_distance - distance

                        # 2. LE VECTEUR NORMAL (La direction de répulsion, de longueur 1)
                        nx = dx / distance
                        ny = dy / distance

                        # 3. LA SÉPARATION PHYSIQUE (On les pousse chacune de la moitié de l'encastrement)
                        transform[id1, 0] -= nx * (overlap / 2.0)
                        transform[id1, 1] -= ny * (overlap / 2.0)

                        transform[id2, 0] += nx * (overlap / 2.0)
                        transform[id2, 1] += ny * (overlap / 2.0)

                        # 4. LA RÉPULSION DES VITESSES (Un vrai rebond de billard !)
                        # Au lieu de juste faire *= -1, l'astuce magique des boules de billard
                        # de même masse, c'est d'ÉCHANGER leurs vitesses !

                        # On sauvegarde temporairement la vitesse de id1
                        temp_vx = velocity[id1, 0]
                        temp_vy = velocity[id1, 1]

                        # id1 prend la vitesse de id2
                        velocity[id1, 0] = velocity[id2, 0]
                        velocity[id1, 1] = velocity[id2, 1]

                        # id2 prend l'ancienne vitesse de id1
                        velocity[id2, 0] = temp_vx
                        velocity[id2, 1] = temp_vy
