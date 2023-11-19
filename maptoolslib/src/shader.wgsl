// Vertex shader

struct CameraUniform {
    campos: vec2<f32>,
};

@group(0) @binding(0)
var<uniform> camera: CameraUniform;

struct VertexInput {
    @location(0) position: vec2<f32>,
    @location(1) colour: vec3<f32>,
};

struct VertexOutput {
     @builtin(position) clip_position: vec4<f32>,
     @location(0) colour: vec3<f32>,
};

@vertex
fn vs_main(
    model: VertexInput,
) -> VertexOutput {
    var out: VertexOutput;
    out.colour = model.colour;
    let screenpos =  model.position - camera.campos;
    out.clip_position = vec4<f32>(screenpos, 0.0, 1.0);
    return out;
}

// Fragment shader

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    return vec4<f32>(in.colour, 1.0);
}
 