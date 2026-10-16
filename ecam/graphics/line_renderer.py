import numpy as np
import wgpu

LINE_SHADER_WGSL = """
struct VertexOutput {
    @builtin(position) pos: vec4f,
    @location(0) color: vec3f,
};

struct VertexInput {
    @location(0) pos: vec2f,    // Position en pixels (X, Y)
    @location(1) color: vec3f,  // Couleur (R, G, B)
};

struct Screen {
    size: vec2f,
};

@group(0) @binding(0) var<uniform> screen: Screen;

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var ndc = (in.pos / screen.size) * 2.0 - 1.0;
    ndc.y = -ndc.y; // Origine en haut à gauche

    var out: VertexOutput;
    out.pos = vec4f(ndc, 0.0, 1.0);
    out.color = in.color;
    return out;
}

@fragment
fn fs_main(@location(0) color: vec3f) -> @location(0) vec4f {
    return vec4f(color, 1.0);
}
"""


class LineRenderer:

    def __init__(
        self,
        device: wgpu.GPUDevice,
        render_texture_format: str,
        screen_size: tuple[int, int] = (1280, 720),
        max_vertices: int = 20_000,
    ):
        self.device = device
        self.screen_width, self.screen_height = screen_size
        self.max_vertices = max_vertices

        # Liste temporaire de sommets accumulés durant la frame
        self._vertices: list[float] = []

        # 1. Shader
        shader = self.device.create_shader_module(code=LINE_SHADER_WGSL)

        # 2. Buffer GPU (5 floats par sommet : X, Y, R, G, B = 20 octets)
        buffer_size = self.max_vertices * 5 * 4
        self.vertex_buffer = self.device.create_buffer(
            size=buffer_size,
            usage=wgpu.BufferUsage.VERTEX | wgpu.BufferUsage.COPY_DST,
        )
        # 2b. Buffer uniform : la taille de l'écran (2 floats = 8 octets)
        self.screen_buffer = self.device.create_buffer(
            size=8,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
        screen_data = np.array([self.screen_width, self.screen_height], dtype=np.float32)
        self.device.queue.write_buffer(self.screen_buffer, 0, screen_data)


        # 3. Layout du buffer (5 floats)
        layout = wgpu.VertexBufferLayout(
            array_stride=20,
            step_mode=wgpu.VertexStepMode.vertex,
            attributes=[
                wgpu.VertexAttribute(
                    format=wgpu.VertexFormat.float32x2,
                    offset=0,
                    shader_location=0,
                ),
                wgpu.VertexAttribute(
                    format=wgpu.VertexFormat.float32x3,
                    offset=8,
                    shader_location=1,
                ),
            ],
        )

        # 4. Pipeline WebGPU en mode LINE_LIST !
        self.pipeline = self.device.create_render_pipeline(
            **wgpu.RenderPipelineDescriptor(
                layout=wgpu.AutoLayoutMode.auto,
                vertex=wgpu.VertexState(
                    module=shader, entry_point="vs_main", buffers=[layout]
                ),
                fragment=wgpu.FragmentState(
                    module=shader,
                    entry_point="fs_main",
                    targets=[
                        wgpu.ColorTargetState(format=render_texture_format)
                    ],
                ),
                # C'EST ICI LE SECRET : mode line_list au lieu de triangles !
                primitive=wgpu.PrimitiveState(
                    topology=wgpu.PrimitiveTopology.line_list
                ),
                depth_stencil=None,
                multisample=None,
            )
        )
        # 5. Bind group : relie le buffer uniform au @group(0) @binding(0) du shader
        self.screen_bind_group = self.device.create_bind_group(
            layout=self.pipeline.get_bind_group_layout(0),
            entries=[
                {
                    "binding": 0,
                    "resource": {"buffer": self.screen_buffer, "offset": 0, "size": 8},
                }
            ],
        )


    def add_line(
        self,
        p1: tuple[float, float],
        p2: tuple[float, float],
        color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> None:
        """Ajoute un segment de ligne à dessiner pour cette frame."""
        # Sommet 1 : [x, y, r, g, b]
        self._vertices.extend([p1[0], p1[1], color[0], color[1], color[2]])
        # Sommet 2 : [x, y, r, g, b]
        self._vertices.extend([p2[0], p2[1], color[0], color[1], color[2]])

    def render(self, render_pass: wgpu.GPURenderPassEncoder) -> None:
        """Envoie les lignes au GPU et les dessine."""
        num_floats = len(self._vertices)
        if num_floats == 0:
            return

        vertex_count = num_floats // 5

        # Envoi direct du tableau au GPU
        data = np.array(self._vertices, dtype=np.float32)
        self.device.queue.write_buffer(self.vertex_buffer, 0, data)

        render_pass.set_pipeline(self.pipeline)
        render_pass.set_bind_group(0, self.screen_bind_group)  # ajouter cette ligne
        render_pass.set_vertex_buffer(0, self.vertex_buffer)
        render_pass.draw(vertex_count)


        # On vide la liste pour la frame suivante !
        self._vertices.clear()