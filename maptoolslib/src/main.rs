use std::num::NonZeroU32;
use wgpu::util::DeviceExt;

// main.rs
#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
struct Vertex {
    position: [f32; 2],
    colour: [f32; 3],
}


async fn run(fp : &str, bgcolour : wgpu::Color) {

    let v1 = Vertex { position: [0.0, 0.5], colour: [1.0, 0.0, 0.0] };
    let v2 = Vertex { position: [-0.2, -0.8], colour: [0.0, 1.0, 1.0] };

    let vertex_data = line2tris(v1,v2, 0.05);
    let verticies = &vertex_data;

    let instance = wgpu::Instance::new(wgpu::Backends::all());
    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::default(),
            compatible_surface: None,
            force_fallback_adapter: false,
        })
        .await
        .unwrap();
    let (device, queue) = adapter
        .request_device(&Default::default(), None)
        .await
        .unwrap();

    let vertex_buffer = device.create_buffer_init(
        &wgpu::util::BufferInitDescriptor {
            label : Some("Vertex Buffer"),
            contents: bytemuck::cast_slice(verticies),
            usage: wgpu::BufferUsages::VERTEX,
        }
    );
    
    
    let vertex_buffer_layout = wgpu::VertexBufferLayout {
        array_stride: std::mem::size_of::<Vertex>() as wgpu::BufferAddress, // 1.
        step_mode: wgpu::VertexStepMode::Vertex, // 2.
        attributes: &[ // 3.
            wgpu::VertexAttribute {
                offset: 0, // 4.
                shader_location: 0, // 5.
                format: wgpu::VertexFormat::Float32x2, // 6.
            },
            wgpu::VertexAttribute {
                offset: std::mem::size_of::<[f32; 2]>() as wgpu::BufferAddress,
                shader_location: 1,
                format: wgpu::VertexFormat::Float32x3,
            }
        ]
    };

    let texture_size = 256u32;//size of square texture
    
    let texture_desc = wgpu::TextureDescriptor {
        size: wgpu::Extent3d {
            width: texture_size,
            height: texture_size,
            depth_or_array_layers: 1,
        },
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8UnormSrgb,
        usage: wgpu::TextureUsages::COPY_SRC | wgpu::TextureUsages::RENDER_ATTACHMENT,
        label: None,
    };
    let texture = device.create_texture(&texture_desc);
    let texture_view = texture.create_view(&Default::default());

    // we need to store this for later
    let u32_size = std::mem::size_of::<u32>() as u32;

    let output_buffer_size = (u32_size * texture_size * texture_size) as wgpu::BufferAddress;
    let output_buffer_desc = wgpu::BufferDescriptor {
        size: output_buffer_size,
        usage: wgpu::BufferUsages::COPY_DST
            // this tells wpgu that we want to read this buffer from the cpu
            | wgpu::BufferUsages::MAP_READ,
        label: None,
        mapped_at_creation: false,
    };
    let output_buffer = device.create_buffer(&output_buffer_desc);

    let shader = device.create_shader_module(&wgpu::ShaderModuleDescriptor {
        label: Some("Vertex Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
    });


    let render_pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: Some("Render Pipeline Layout"),
        bind_group_layouts: &[],
        push_constant_ranges: &[],
    });

    

    let render_pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Render Pipeline"),
        layout: Some(&render_pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[vertex_buffer_layout],
        },
        fragment: Some(wgpu::FragmentState {
            module: &shader,
            entry_point: "fs_main",
            targets: &[wgpu::ColorTargetState {
                format: texture_desc.format,
                blend: Some(wgpu::BlendState {
                    alpha: wgpu::BlendComponent::REPLACE,
                    color: wgpu::BlendComponent::REPLACE,
                }),
                write_mask: wgpu::ColorWrites::ALL,
            }],
        }),
        primitive: wgpu::PrimitiveState {
            topology: wgpu::PrimitiveTopology::TriangleList,
            strip_index_format: None,
            front_face: wgpu::FrontFace::Ccw,
            cull_mode: None,
            // Setting this to anything other than Fill requires Features::NON_FILL_POLYGON_MODE
            polygon_mode: wgpu::PolygonMode::Fill,
            // Requires Features::DEPTH_CLAMPING
            clamp_depth: false,
            // Requires Features::CONSERVATIVE_RASTERIZATION
            conservative: false,
        },
        depth_stencil: None,
        multisample: wgpu::MultisampleState {
            count: 1,
            mask: !0,
            alpha_to_coverage_enabled: false,
        },
    });

    let mut encoder =
        device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None });

    {
        let render_pass_desc = wgpu::RenderPassDescriptor {
            label: Some("Render Pass"),
            color_attachments: &[wgpu::RenderPassColorAttachment {
                view: &texture_view,
                resolve_target: None,
                ops: wgpu::Operations {
                    load: wgpu::LoadOp::Clear(bgcolour),
                    store: true,
                },
            }],
            depth_stencil_attachment: None,
        };
        let mut render_pass = encoder.begin_render_pass(&render_pass_desc);

        render_pass.set_pipeline(&render_pipeline);
        
        render_pass.set_vertex_buffer(0, vertex_buffer.slice(..));
        render_pass.draw(0..(verticies.len() as u32), 0..1);
    }

    encoder.copy_texture_to_buffer(
        wgpu::ImageCopyTexture {
            aspect: wgpu::TextureAspect::All,
            texture: &texture,
            mip_level: 0,
            origin: wgpu::Origin3d::ZERO,
        },
        wgpu::ImageCopyBuffer {
            buffer: &output_buffer,
            layout: wgpu::ImageDataLayout {
                offset: 0,
                bytes_per_row: NonZeroU32::new(u32_size * texture_size),
                rows_per_image: NonZeroU32::new(texture_size),
            },
        },
        texture_desc.size,
    );

    queue.submit(Some(encoder.finish()));
    
    let buffer_slice = output_buffer.slice(..);

    // NOTE: We have to create the mapping THEN device.poll() before await
    // the future. Otherwise the application will freeze.
    let mapping = buffer_slice.map_async(wgpu::MapMode::Read);
    device.poll(wgpu::Maintain::Wait);
    mapping.await.unwrap();

    save_buffer(&buffer_slice, texture_size, fp);
    
    
    output_buffer.unmap();
}

fn save_buffer(buffer_slice : &wgpu::BufferSlice, texture_size : u32, fp : &str ){

    let data = buffer_slice.get_mapped_range();

    use image::{ImageBuffer, Rgba};
    let buffer =
        ImageBuffer::<Rgba<u8>, _>::from_raw(texture_size, texture_size, data).unwrap();
    buffer.save(fp).unwrap();
}


fn main() {
    let fp = "outfile.png";
    let bgcolour = wgpu::Color {r: 0.1, g: 0.1, b: 0.1, a: 1.0,};

    pollster::block_on(run(fp , bgcolour));
}



fn invgrad(from : Vertex,to : Vertex) -> f32{
    let x1 : f32 = from.position[0];
    let y1 : f32 = from.position[1];
    
    let x2 : f32 = to.position[0];
    let y2 : f32 = to.position[1];
    
    if y1 == y2 {
        return f32::MAX;
    }else{
        return -(x1-x2)/(y1-y2);
    }
}

fn sub(from : Vertex,to : Vertex) -> Vertex{
    let x1 : f32 = from.position[0];
    let y1 : f32 = from.position[1];    
    
    let x2 : f32 = to.position[0];
    let y2 : f32 = to.position[1];
    
    let col = from.colour;
    
   return Vertex {position: [x1 - x2, y1-y2], colour: col};
}

fn add(from : Vertex,to : Vertex) -> Vertex{
    let x1 : f32 = from.position[0];
    let y1 : f32 = from.position[1];
    
    let x2 : f32 = to.position[0];
    let y2 : f32 = to.position[1];
    
    let col = from.colour;
    
   return Vertex {position: [x1 + x2, y1+y2], colour: col};
}

fn mul(v : Vertex, s : f32) -> Vertex{
    let x : f32 = v.position[0];
    let y : f32 = v.position[1];
    
    let col = v.colour;
    
    return Vertex {position: [x*s, y*s], colour: col};
}

fn norm(v : Vertex) -> Vertex{
    let x : f32 = v.position[0];
    let y : f32 = v.position[1];

    let n : f32 = (x*x + y*y).sqrt();
    
    let col = v.colour;
    
    return Vertex {position: [x/n, y/n], colour: col};
    

}

fn normal(from : Vertex,to : Vertex) -> Vertex{
    
    let g : f32 = invgrad(from,to);
    
    let col = from.colour;
    
    let normal;
    if g != f32::MAX{
        normal = Vertex {position : [1.0, g], colour: col};
    }else{
        normal = Vertex {position : [0.0,1.0], colour: col};
    }
        
    return norm(normal);
    
}

fn line2tris(from : Vertex,to : Vertex, width : f32) -> [Vertex; 6]{
    
    let normal: Vertex = normal(from, to);
    let ofset : Vertex = mul(normal,width/2.0);
    
    let v1 : Vertex = add(from, ofset);
    let v2 : Vertex = sub(from, ofset);
    
    let v3 : Vertex = add(to, ofset);
    let v4 : Vertex = sub(to, ofset);

    return [v1,v3,v2,v3,v4,v2];
}