# Dans ecam/app.py

from rendercanvas.auto import RenderCanvas, loop
import wgpu

from ecam.core.system          import System
from ecam.core.clock           import Clock
from ecam.core.input           import InputManager
from ecam.core.registry        import Registry
from ecam.core.types           import EntityID, FLOAT32, UINT32
from ecam.graphics.render_system import RenderSystem
from ecam.graphics.line_renderer import LineRenderer


class App:

    def __init__(
        self,
        title: str = "ECAM Game",
        width: int = 1280,
        height: int = 720,
        max_fps: int = 90,
    ):
        self.width = width
        self.height = height

        # 1. Matériel WebGPU
        self.adapter = wgpu.gpu.request_adapter_sync()
        self.device = self.adapter.request_device_sync()

        # 2. Fenêtre Canvas
        self.canvas = RenderCanvas(
            size=(width, height), title=title, max_fps=max_fps
        )
        self.context = self.canvas.get_wgpu_context()
        self.render_format = self.context.get_preferred_format(
            self.device.adapter
        )
        self.context.configure(device=self.device, format=self.render_format)

        # 3. Le Cœur ECS
        self.ecs = Registry(MAX_ENTITIES=20_000)
        # Composants de base déclarés automatiquement
        self.ecs.register_component("Transform", FLOAT32, (2,))
        self.ecs.register_component("Velocity", FLOAT32, (2,))
        self.ecs.register_component("BoxCollider", FLOAT32, (2,))
        self.ecs.register_component("CollisionFilter", UINT32, (4,))
        self.ecs.register_component("GravityScale", FLOAT32, (1,))

        self.render_system = RenderSystem( # Init le system de rendu
            self.ecs, self.device, self.render_format, (width, height)
        )
        self.line_renderer = LineRenderer( # Init le system de dessin de lignes
            self.device, self.render_format, (width, height)
        )

        # 5. Outils : Temps et Inputs
        self.clock = Clock()
        self.inputs = InputManager()
        self.inputs.bind_to_canvas(self.canvas)

    # ------------------------------------------------------------------
    # MÉTHODES DE CONFORT POUR LE JOUEUR / BINÔME
    # ------------------------------------------------------------------
    def spawn(
        self,
        pos: tuple[float, float],
        size: tuple[float, float] = (16.0, 16.0),
        vel: tuple[float, float] = (0.0, 0.0),
        is_static: bool = False,
        is_trigger: bool = False,
        layer: int = 1,
        mask: int = 0xFFFFFFFF,
    ) -> EntityID:
        eid = self.ecs.create_entity()
        hw, hh = size[0] / 2.0, size[1] / 2.0
        g_scale = 0.0 if is_static else 1.0
        initial_vel = (0.0, 0.0) if is_static else vel

        self.ecs.add_component(
            eid,
            ("Transform", pos),
            ("Velocity", initial_vel),
            ("BoxCollider", (hw, hh)),
            ("CollisionFilter", (int(is_trigger), int(is_static), layer, mask)),
            ("GravityScale", (g_scale,))
        )
        return eid
    

    def add_system(self, system: System) -> System:
        """Permet à l'utilisateur d'ajouter un système dans la boucle automatique."""
        return self.ecs.add_system(system)
    

    def draw_line(
       self,
       p1: tuple[float, float],
       p2: tuple[float, float],
       color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> None:
       """Trace une ligne entre p1 et p2."""
       self.line_renderer.add_line(p1, p2, color)


    # ------------------------------------------------------------------
    # MÉTHODES À SURCHARGER PAR LE BINÔME (Comme dans Pygame !)
    # ------------------------------------------------------------------
    def on_init(self):
        """Appelée une seule fois au démarrage."""
        pass

    def on_update(self, dt: float):
        """Appelée à chaque frame pour le gameplay."""
        pass
    
    def on_finish(self):
        """Appelée une seule fois a la fermeture de la fenetre"""
        pass
    
    # ------------------------------------------------------------------
    # LA BOUCLE INTERNE (Cachée sous le capot)
    # ------------------------------------------------------------------
    def _frame_loop(self):
        dt = self.clock.tick()

        # A. Mise à jour des systems declarer par le user
        self.ecs.update_systems(dt)

        # B. Gameplay de l'utilisateur
        self.on_update(dt)

        # C. Rendu WebGPU
        encoder = self.device.create_command_encoder()
        view = self.context.get_current_texture().create_view()
        pass_render = encoder.begin_render_pass(
            color_attachments=[
                wgpu.RenderPassColorAttachment(
                    view=view,
                    clear_value=(0.08, 0.08, 0.1, 1.0),
                    load_op=wgpu.LoadOp.clear,
                    store_op=wgpu.StoreOp.store,
                )
            ]
        )

        self.render_system.render(pass_render)
        self.line_renderer.render(pass_render)
        pass_render.end()
        self.device.queue.submit([encoder.finish()])

        # D. Nettoyage des événements one-shot de la frame
        self.inputs.clear_frame_inputs()

        # Frame suivante
        self.canvas.request_draw()

    def run(self):
        """Démarre le jeu."""
        self.on_init()
        self.canvas.request_draw(self._frame_loop)
        loop.run()
        self.on_finish()