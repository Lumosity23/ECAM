import time
import numpy as np
from rendercanvas.auto import RenderCanvas, loop
import wgpu

from ecam import MovementSystem, BoundarySystem, Registry, FLOAT32, RenderSystem, Clock, Profiler

# ----------------------------------------------------------------------
# 1. INITIALISATION DE LA FENÊTRE ET DE WEBGPU
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720

clock = Clock()
adapter = wgpu.gpu.request_adapter_sync()
device = adapter.request_device_sync()

canvas = RenderCanvas(
    size=(WIDTH, HEIGHT),
    vsync=False,
    max_fps=1000,
    title="ECAM - Test Carré WebGPU")

context = canvas.get_wgpu_context()
render_texture_format = context.get_preferred_format(device.adapter)
context.configure(device=device, format=render_texture_format)

# ----------------------------------------------------------------------
# 2. INITIALISATION DE L'ECS (Ton Core !)
# ----------------------------------------------------------------------
ecs = Registry(MAX_ENTITIES=30_000)
profiler = Profiler()

# Enregistrement des composants
ecs.register_component("Transform", FLOAT32, (2,))  # Position (X, Y)
ecs.register_component("Velocity", FLOAT32, (2,))  # Vitesse (VX, VY)

# Ajout du système de mouvement (avec une petite gravité vers le bas pour le fun)
movement_system = MovementSystem(ecs, gravity=(0.0, 200.0))
boundary_system = BoundarySystem(
    ecs, bounds=(0, 0, WIDTH, HEIGHT), restitution=0.8, mode="bounce"
)

# ----------------------------------------------------------------------
# 3. CRÉATION D'UNE ENTITÉ (Notre Carré)
# ----------------------------------------------------------------------
# On fait naître une entité au centre de l'écran avec une vitesse initiale
N = 30000

# Enregistre aussi le BoxCollider (taille 16x16 -> demi-taille 8x8)
ecs.register_component("BoxCollider", FLOAT32, (2,))

for _ in range(N):
    eid = ecs.create_entity(0)
    rx = np.random.uniform(100, WIDTH - 100)
    ry = np.random.uniform(50, 300)
    vx = np.random.uniform(-300, 300)
    vy = np.random.uniform(-100, 100)
    ecs.add_component(
        eid,
        ("Transform", (rx, ry)),
        ("Velocity", (vx, vy)),
        ("BoxCollider", (8.0, 8.0)),  # 16x16 pixels
    )

# ----------------------------------------------------------------------
# 4. INITIALISATION DU RENDER SYSTEM WEBGPU
# ----------------------------------------------------------------------
render_system = RenderSystem(
    registry=ecs,
    device=device,
    render_texture_format=render_texture_format,
    screen_size=(WIDTH, HEIGHT),
)

# ----------------------------------------------------------------------
# 5. LA BOUCLE DE JEU (Logique ECS + Rendu WebGPU)
# ----------------------------------------------------------------------
last_time = time.perf_counter()


def game_loop():

    # A. Calcul du Delta Time (dt)
    dt = clock.tick()

    # B. LOGIQUE ECS : Mise à jour de la physique
    with profiler.measure("Logic"):
        movement_system.update(dt)
        boundary_system.update(dt)

    # C. PRÉPARATION DU RENDU WEBGPU
    with profiler.measure("Render"):
        command_encoder = device.create_command_encoder()
        current_texture_view = context.get_current_texture().create_view()

        # Début de la passe de rendu avec fond sombre (gris bleuté)
        render_pass = command_encoder.begin_render_pass(
            color_attachments=[
                wgpu.RenderPassColorAttachment(
                    view=current_texture_view,
                    clear_value=(0.08, 0.08, 0.1, 1.0),  # Fond sombre
                    load_op=wgpu.LoadOp.clear,
                    store_op=wgpu.StoreOp.store,
                )
            ]
        )

        # D. APPEL DU RENDER SYSTEM D'ECAM
        render_system.render(render_pass)

        # Fin de la passe et soumission à la carte graphique
        render_pass.end()
        device.queue.submit([command_encoder.finish()])

    
    # Temps total de travail CPU + GPU
    total_work_ms = profiler.get_ms("Logic") + profiler.get_ms("Render")

    # Estimation du potentiel maximal sans aucune bride :
    fps_potentiel = 1000.0 / max(0.001, total_work_ms)

    # Si tu es en VSync (autour de 90 FPS) :
    budget_ms = 16.66  # pour 90 Hz
    marge_libre = max(0.0, (1.0 - (total_work_ms / budget_ms)) * 100.0)

    canvas.set_title(
        f"FPS: {clock.fps:.0f} (Potentiel max: {fps_potentiel:.0f}) | "
        f"Travail: {total_work_ms:.2f}ms | "
        f"Marge libre: {marge_libre:.1f}% | "
        f"Entités: {ecs.count}"
    )

    # Demander la prochaine frame pour que l'animation soit fluide et continue
    canvas.request_draw()


# On enregistre notre boucle de jeu et on démarre l'application
canvas.request_draw(game_loop)

if __name__ == "__main__":
    loop.run()