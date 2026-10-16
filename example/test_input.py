from ecam import App, MovementSystem


class Game_test(App):

    def on_init(self):
        # Il spawne son joueur en 1 ligne !
        self.player = self.spawn(pos=(640, 360), size=(32, 32))
        self.spawn(pos=(640, 500), size=(300, 30), vel=(0,0))
        
        self.movement_system = self.add_system(MovementSystem(self.ecs, (0.0, 400.0)))
        

    def on_update(self, dt: float):
        # Récupère la vitesse du joueur
        idx = self.ecs.index_of(self.player)
        vel = self.ecs.components["Velocity"]

        # Contrôles clavier intuitifs :
        if self.inputs.is_key_down("ArrowRight"):
            vel[idx, 0] = 200.0
        elif self.inputs.is_key_down("ArrowLeft"):
            vel[idx, 0] = -200.0
        else:
            vel[idx, 0] = 0.0  # Arrêt

        # Saut : seulement quand on APPUIE sur Espace (just_pressed)
        if self.inputs.just_pressed("Space"):
            vel[idx, 1] = -300.0  # Impulsion vers le haut
            


if __name__ == "__main__":
    Game_test(title="Mon Jeu ECAM", width=1280, height=720).run()