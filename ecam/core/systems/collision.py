import numpy as np

from ..system import System
from ..types import EntityID


class CollisionSystem(System):

    def __init__(self, registry):
        super().__init__(registry)

    def update(self, dt: float) -> None:
        count = self.registry.count
        if count <= 1:
            return

        # 1. On récupère les tableaux nécessaires
        mask = self.registry.get_mask(
            "Transform", "BoxCollider", "CollisionFilter"
        )
        is_valid = self.registry.query(mask)

        transform = self.registry.components["Transform"][:count]
        box = self.registry.components["BoxCollider"][:count]
        filters = self.registry.components["CollisionFilter"][:count]

        # On a aussi besoin de Velocity pour stopper les objets contre les murs
        has_vel = "Velocity" in self.registry.components
        vel = self.registry.components["Velocity"][:count] if has_vel else None

        # 2. Séparation des Solides et des Triggers
        # is_trigger == 0 signifie SOLIDE
        is_solid = (filters[:, 0] == 0) & is_valid
        solid_indices = np.where(is_solid)[0]

        # S'il y a des solides, on résout les collisions entre eux
        for i_idx, a_idx in enumerate(solid_indices):
            # Pour chaque solide A, on teste les solides B suivants
            for b_idx in solid_indices[i_idx + 1 :]:

                # Filtre de calque (Layer & Mask)
                layer_a, mask_a = filters[a_idx, 1], filters[a_idx, 2]
                layer_b, mask_b = filters[b_idx, 1], filters[b_idx, 2]

                # Est-ce qu'ils ont le droit d'interagir ?
                if (layer_a & mask_b == 0) and (layer_b & mask_a == 0):
                    continue

                # Calcul des distances entre centres
                dx = transform[a_idx, 0] - transform[b_idx, 0]
                dy = transform[a_idx, 1] - transform[b_idx, 1]

                # Calcul des demi-tailles cumulées
                total_hw = box[a_idx, 0] + box[b_idx, 0]
                total_hh = box[a_idx, 1] + box[b_idx, 1]

                # Calcul de l'enfoncement (Overlap)
                ox = total_hw - abs(dx)
                oy = total_hh - abs(dy)

                # Dans ecam/core/collision_system.py, au moment de tester ox < oy :

                if ox > 0 and oy > 0:
                    vx = vel[a_idx, 0] if vel is not None else 0.0
                    vy = vel[a_idx, 1] if vel is not None else 0.0

                    # 1. Le joueur se déplace-t-il VERS l'obstacle en X ?
                    # (dx > 0 signifie que A est à droite de B, donc aller à gauche vx < 0 rapproche de B)
                    moving_towards_x = (dx < 0 and vx > 0) or (dx > 0 and vx < 0)

                    # 2. Le joueur se déplace-t-il VERS l'obstacle en Y ?
                    # (dy < 0 signifie que A est AU-DESSUS de B, donc descendre vy > 0 rapproche de B)
                    # (dy > 0 signifie que A est EN-DESSOUS de B, donc monter vy < 0 heurte le plafond)
                    moving_towards_y = (dy < 0 and vy > 0) or (dy > 0 and vy < 0)

                    # 3. DÉCISION DE RÉSOLUTION :
                    if moving_towards_x and not moving_towards_y:
                        # On va vers le mur mais PAS vers le sol/plafond -> Résolution X obligatoire !
                        resolve_x = True
                    elif moving_towards_y and not moving_towards_x:
                        # On tombe sur le sol ou heurte le plafond sans pousser sur le côté -> Résolution Y obligatoire !
                        resolve_x = False
                    else:
                        # Les deux axes poussent (ou aucun) -> On prend le plus petit enfoncement (MTV standard)
                        resolve_x = ox < oy

                    # 4. APPLICATION DE LA RÉPULSION :
                    is_static_a = filters[a_idx, 1] == 1
                    is_static_b = filters[b_idx, 1] == 1

                    if is_static_a and is_static_b:
                        continue
                    
                    # Qui doit être repoussé ?
                    # Si A est statique -> c'est B qui doit reculer (en sens inverse) !
                    # Si B est statique (ou aucun des deux) -> c'est A qui recule !
                    target_idx = b_idx if is_static_a else a_idx
                    direction_mult = -1.0 if is_static_a else 1.0

                    if resolve_x:
                        sign_x = (1.0 if dx > 0 else -1.0) * direction_mult
                        transform[target_idx, 0] += ox * sign_x
                        if vel is not None:
                            vel[target_idx, 0] = 0.0
                    else:
                        sign_y = (1.0 if dy > 0 else -1.0) * direction_mult
                        transform[target_idx, 1] += oy * sign_y
                        if vel is not None:
                            vel[target_idx, 1] = 0.0


    # ------------------------------------------------------------------
    # MÉTHODE D'OVERLAP POUR LES TRIGGERS (Pièces, Balles, Zones)
    # ------------------------------------------------------------------
    def get_overlapping_entities(
        self, entity_id: EntityID, target_layer: int | None = None
    ) -> list[EntityID]:
        """Retourne la liste des entités qui touchent l'entité donnée (vectorisé en NumPy)."""
        idx = self.registry.index_of(entity_id)  # -1 si l'entité est morte
        if idx == -1:
            return []

        count = self.registry.count
        transform = self.registry.components["Transform"][:count]
        box = self.registry.components["BoxCollider"][:count]
        filters = self.registry.components["CollisionFilter"][:count]

        # Coordonnées de l'entité cible
        x, y = transform[idx]
        hw, hh = box[idx]

        # Calcul vectorisé NumPy contre TOUT LE MONDE à la fois !
        dx = np.abs(transform[:, 0] - x)
        dy = np.abs(transform[:, 1] - y)
        ox = (box[:, 0] + hw) - dx
        oy = (box[:, 1] + hh) - dy

        # Masque de collision
        colliding = (ox > 0) & (oy > 0)
        # On ne se touche pas soi-même !
        colliding[idx] = False

        # Filtre optionnel sur le calque
        if target_layer is not None:
            colliding &= (filters[:, 1] & target_layer) != 0

        # Récupération des IDs stables grâce au tableau dense
        valid_dense_indices = np.where(colliding)[0]
        return [self.registry.entity_at(i) for i in valid_dense_indices]