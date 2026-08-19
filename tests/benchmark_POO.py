import pygame
import random
import time

# ----------------------------------------------------
# L'APPROCHE POO CLASSIQUE (L'Objet au centre de tout)
# ----------------------------------------------------
class Ball:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = (33, 91, 99) # BK_LIGHTBLUE
        self.size = 10

    def update(self, dt, screen_width, screen_height):
        # 1. On applique la vitesse
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 2. Les rebonds
        if self.y >= screen_height:
            self.y = screen_height
            self.vy *= -0.8
        elif self.y <= 0:
            self.y = 0
            self.vy *= -1.0

        if self.x >= screen_width:
            self.x = screen_width
            self.vx *= -0.8
        elif self.x <= 0:
            self.x = 0
            self.vx *= -0.8

    def draw(self, screen):
        # Rendu individuel
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)


def main():
    pygame.init()
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    # On crée une liste de 10 000 objets "Ball"
    print("Création des 10 000 objets... (Ça peut prendre un instant)")
    balls = []
    for _ in range(10000):
        b = Ball(
            x = screen_width / 2, 
            y = screen_height / 2, 
            vx = random.uniform(-500, 500), 
            vy = random.uniform(-500, 500)
        )
        balls.append(b)

    running = True
    while running:
        dt = clock.tick(0) / 1000.0 # tick(0) désactive la limite de FPS !

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- CHRONO DE LA LOGIQUE ---
        
        
        # Le cauchemar du processeur : La boucle FOR en Python pur
        for b in balls:
            b.update(dt, screen_width, screen_height)
            
        

        start_time = time.perf_counter()
        # --- RENDU ---
        screen.fill((0, 0, 0))
        for b in balls:
            b.draw(screen)
        logic_time = (time.perf_counter() - start_time) * 1000 # En millisecondes

        # Affichage du framerate
        fps = clock.get_fps()
        pygame.display.set_caption(f"POO Benchmark - FPS: {int(fps)} | Temps Logique: {logic_time:.2f} ms")
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()