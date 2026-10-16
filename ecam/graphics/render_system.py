# ecam/graphics/render_system.py

import numpy as np
import wgpu

from ecam.core.system import System

SPRITE_SHADER_WGSL = """
struct VertexOutput {
    @builtin(position) pos: vec4f,
};

struct VertexInput {
    @location(0) instance_pos: vec2f,
    @location(1) instance_size: vec2f, // Largeur et Hauteur réelles
};

struct Screen {
    size: vec2f,
};

@group(0) @binding(0) var<uniform> screen: Screen;

@vertex
fn vs_main(
    @builtin(vertex_index) v_idx: u32,
    in: VertexInput
) -> VertexOutput {
    // 6 sommets d'un quad centré (-0.5 à +0.5)
    var quad = array<vec2f, 6>(
        vec2f(-0.5, -0.5), vec2f( 0.5, -0.5), vec2f(-0.5,  0.5),
        vec2f(-0.5,  0.5), vec2f( 0.5, -0.5), vec2f( 0.5,  0.5)
    );

    // Position en pixels : Centre + (Coin * Taille)
    let pixel_pos = in.instance_pos + (quad[v_idx] * in.instance_size);

    // Conversion en coordonnées NDC (-1.0 à 1.0)
    var ndc = (pixel_pos / screen.size) * 2.0 - 1.0;
    ndc.y = -ndc.y; // Origine en haut à gauche

    var out: VertexOutput;
    out.pos = vec4f(ndc, 0.0, 1.0);
    return out;
}

@fragment
fn fs_main() -> @location(0) vec4f {
    // Couleur saumon / rougeâtre par défaut
    return vec4f(1.0, 0.4, 0.3, 1.0);
}
"""


class RenderSystem(System):

    def __init__(
        self,
        registry,
        device: wgpu.GPUDevice,
        render_texture_format: str,
        screen_size: tuple[int, int] = (1280, 720),
    ):
        super().__init__(registry)
        self.device = device
        self.screen_width, self.screen_height = screen_size

        # 1. Compilation du Shader WGSL
        shader = self.device.create_shader_module(code=SPRITE_SHADER_WGSL)

        # 2. Création de l'INSTANCE BUFFER (4 floats par entité : X, Y, W, H)
        # 4 floats * 4 octets = 16 octets par entité
        buffer_size = self.registry.MAX_ENTITIES * 4 * 4
        self.instance_buffer = self.device.create_buffer(
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



        # 3. Layout mémoire du buffer d'instances
        instance_buffer_layout = wgpu.VertexBufferLayout(
            array_stride=16,  # 16 octets par entité
            step_mode=wgpu.VertexStepMode.instance,
            attributes=[
                # @location(0) : Position (X, Y)
                wgpu.VertexAttribute(
                    format=wgpu.VertexFormat.float32x2,
                    offset=0,
                    shader_location=0,
                ),
                # @location(1) : Taille (W, H)
                wgpu.VertexAttribute(
                    format=wgpu.VertexFormat.float32x2,
                    offset=8,  # Après les 8 premiers octets
                    shader_location=1,
                ),
            ],
        )

        # 4. Le Pipeline de rendu
        self.pipeline = self.device.create_render_pipeline(
            **wgpu.RenderPipelineDescriptor(
                layout=wgpu.AutoLayoutMode.auto,
                vertex=wgpu.VertexState(
                    module=shader,
                    entry_point="vs_main",
                    buffers=[instance_buffer_layout],
                ),
                fragment=wgpu.FragmentState(
                    module=shader,
                    entry_point="fs_main",
                    targets=[
                        wgpu.ColorTargetState(format=render_texture_format)
                    ],
                ),
                primitive=wgpu.PrimitiveState(
                    topology=wgpu.PrimitiveTopology.triangle_list
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


    def update(self, dt: float) -> None:
        pass

    def render(self, render_pass: wgpu.GPURenderPassEncoder) -> None:
        count = self.registry.count
        if count == 0:
            return

        transform = self.registry.components["Transform"][:count]

        # Récupération des tailles réelles (BoxCollider * 2 car ce sont des demi-tailles)
        if "BoxCollider" in self.registry.components:
            box = self.registry.components["BoxCollider"][:count]
            sizes = box * 2.0
        else:
            sizes = np.full((count, 2), 16.0, dtype=np.float32)

        # Assemblage de [X, Y, W, H] dans un bloc mémoire contigu
        instance_data = np.empty((count, 4), dtype=np.float32)
        instance_data[:, 0:2] = transform
        instance_data[:, 2:4] = sizes

        # Envoi direct vers self.instance_buffer (VRAM)
        self.device.queue.write_buffer(self.instance_buffer, 0, instance_data)

        # Commandes de dessin
        render_pass.set_pipeline(self.pipeline)
        render_pass.set_bind_group(0, self.screen_bind_group)  # ajouter cette ligne
        render_pass.set_vertex_buffer(0, self.instance_buffer)
        render_pass.draw(6, count)
