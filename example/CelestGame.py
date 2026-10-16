from ecam import App, MovementSystem, CollisionSystem


class CelesteGame(App):

    def on_init(self):
        # 1. ON CHOISIT EXACTEMENT NOS SYSTÈMES :
        # On veut la physique avec gravité :
        self.movement = self.add_system(
            MovementSystem(self.ecs, gravity=(0.0, 800.0))
        )
        # On veut les collisions avec les plateformes :
        self.collisions = self.add_system(CollisionSystem(self.ecs))

        # Remarque : PAS DE BOUNDARY SYSTEM ! Si on tombe dans le trou, on tombe !

        # 2. Spawns
        self.player = self.spawn(pos=(200, 200), size=(24, 32))
        self.sol = self.spawn(pos=(640, 600), size=(1000, 40), is_static=True)
        self.plateforme = self.spawn(pos=(500, 450), size=(200, 20), is_static=True)


    def on_update(self, dt: float):
        # Controlle de Madeline
        idx = self.ecs.sparse[self.player]
        vel = self.ecs.components["Velocity"]

        if self.inputs.just_pressed("Space"):
            vel[idx, 1] = -300

        if self.inputs.is_key_down("ArrowRight"):
            vel[idx, 0] = 200.0
        elif self.inputs.is_key_down("ArrowLeft"):
            vel[idx, 0] = -200.0
        else:
            vel[idx, 0] = 0.0




if __name__ == "__main__":
    CelesteGame().run()