use std::num::NonZeroU32;
use std::iter;
use wgpu::util::DeviceExt;

use crate::draw::{TILESIZE, TEXSIZE};

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
pub struct Vertex {
    position: [f32; 2],
    colour: [f32; 3],
}

#[repr(C)]
#[derive(Debug, Copy, Clone, bytemuck::Pod, bytemuck::Zeroable)]
struct CameraUniform {
    campos: [f32; 2],
}




fn make_render_pipeline(device : &wgpu::Device, vbuff_layout : wgpu::VertexBufferLayout, cbg_layout: wgpu::BindGroupLayout, texture_desc : &wgpu::TextureDescriptor) -> wgpu::RenderPipeline{
    let shader = device.create_shader_module(&wgpu::ShaderModuleDescriptor {
        label: Some("Vertex Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
    });

    let render_pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: Some("Render Pipeline Layout"),
        bind_group_layouts: &[&cbg_layout],
        push_constant_ranges: &[],
    });

    let render_pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Render Pipeline"),
        layout: Some(&render_pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[vbuff_layout],
        },
        fragment: Some(wgpu::FragmentState {
            module: &shader,
            entry_point: "fs_main",
            targets: &[wgpu::ColorTargetState {
                format: texture_desc.format,
                blend: Some(wgpu::BlendState {
                    alpha: wgpu::BlendComponent::OVER,
                    color: wgpu::BlendComponent::OVER,
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
            // Requires Features::DEPTH_CLIP_CONTROL
            unclipped_depth: false,
            // Requires Features::CONSERVATIVE_RASTERIZATION
            conservative: false,
        },
        depth_stencil: None,
        multisample: wgpu::MultisampleState {
            count: 4,
            mask: !0,
            alpha_to_coverage_enabled: true,
        },
        multiview: None,
    });
    
    return render_pipeline;
}

pub struct Graphics {
    dev : wgpu::Device,
    que : wgpu::Queue,
    obff : wgpu::Buffer,
    rpl : wgpu::RenderPipeline,
    tex : wgpu::Texture,
    texaa : wgpu::Texture,
    texsz : u32,
    texmemsz : wgpu::Extent3d,
    vbff: Option<wgpu::Buffer>,
    vbffsz: u32,
    cbff: wgpu::Buffer,
    cbg: wgpu::BindGroup,
}


pub async fn setup() -> Graphics{
    // // // // // // // instance
    let instance = wgpu::Instance::new(wgpu::Backends::all());
    // // // // // // // make new adapter
    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::default(),
            compatible_surface: None,
            force_fallback_adapter: false,
        })
        .await
        .unwrap();
    // // // // // // // make new device and queue    
    let (device, queue) = adapter
        .request_device(&Default::default(), None)
        .await
        .unwrap();
    // // // // // // // set vertex buffer layout
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

    // // // // // // set camera buffer 
    let camera_uniform = CameraUniform{campos : [0.0,0.0]
    };

    let camera_buffer = device.create_buffer_init(
        &wgpu::util::BufferInitDescriptor {
            label: Some("Camera Buffer"),
            contents: bytemuck::cast_slice(&[camera_uniform]),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        }
    );


    let camera_bind_group_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
        entries: &[
            wgpu::BindGroupLayoutEntry {
                binding: 0,
                visibility: wgpu::ShaderStages::VERTEX,
                ty: wgpu::BindingType::Buffer {
                    ty: wgpu::BufferBindingType::Uniform,
                    has_dynamic_offset: false,
                    min_binding_size: None,
                },
                count: None,
            }
        ],
        label: Some("camera_bind_group_layout"),
    });

    let camera_bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
        layout: &camera_bind_group_layout,
        entries: &[
            wgpu::BindGroupEntry {
                binding: 0,
                resource: camera_buffer.as_entire_binding(),
            }
        ],
        label: Some("camera_bind_group"),
    });
     

    // // // // // // // output texture setup 
    let tex_size = TEXSIZE as u32;

    let tex_mem_size = wgpu::Extent3d {
        width: tex_size,
        height: tex_size,
        depth_or_array_layers: 1,
    };
    let tex_desc_msaa =  wgpu::TextureDescriptor {
        size: tex_mem_size,
        mip_level_count: 1,
        sample_count: 4,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8UnormSrgb,
        usage: wgpu::TextureUsages::COPY_SRC | wgpu::TextureUsages::RENDER_ATTACHMENT,
        label: None,
    };

    let tex_desc = wgpu::TextureDescriptor {
        size: tex_mem_size,
        mip_level_count: 1,
        sample_count: 1,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8UnormSrgb,
        usage: wgpu::TextureUsages::COPY_SRC | wgpu::TextureUsages::RENDER_ATTACHMENT,
        label: None,
    };

    let texture_msaa = device.create_texture(&tex_desc_msaa);
    let texture = device.create_texture(&tex_desc);

    // // // // // // make output buffer
    let u32_size = std::mem::size_of::<u32>() as u32;
    let output_buffer_size = (u32_size * tex_size * tex_size) as wgpu::BufferAddress;
    let output_buffer_desc = wgpu::BufferDescriptor {
        size: output_buffer_size,
        usage: wgpu::BufferUsages::COPY_DST
            // this tells wpgu that we want to read this buffer from the cpu
            | wgpu::BufferUsages::MAP_READ,
        label: None,
        mapped_at_creation: false,
    };
    let output_buffer = device.create_buffer(&output_buffer_desc);

    // // // // // // setup rendering pipeline
    let render_pipeline = make_render_pipeline(&device, vertex_buffer_layout, camera_bind_group_layout, &tex_desc);

    
    let graphics = Graphics {
        dev : device,
        que : queue,
        obff : output_buffer,
        rpl : render_pipeline,
        tex : texture,
        texaa : texture_msaa,
        texsz : tex_size,
        texmemsz : tex_mem_size,
        vbff : None,
        vbffsz : 0,
        cbg : camera_bind_group,
        cbff : camera_buffer,
    };
    return graphics;
}

pub fn setvertdata(graphics : &mut Graphics, verticies : &Vec<Vertex>){
    // // // // // // set vertex buffer
    let vertex_buffer = graphics.dev.create_buffer_init(
        &wgpu::util::BufferInitDescriptor {
            label : Some("Vertex Buffer"),
            contents: bytemuck::cast_slice(verticies),
            usage: wgpu::BufferUsages::VERTEX,
        }
    );

    graphics.vbff = Some(vertex_buffer);
    graphics.vbffsz = verticies.len() as u32;
}


pub async fn run(graphics : &Graphics, tile: [i32;2], bgcolour : [f32;4], fp : &str) {    
    let vbff = graphics.vbff.as_ref().unwrap();
    // // // // // // // background colour
    let bgcolour = wgpu::Color {
        r: bgcolour[0] as f64, 
        g: bgcolour[1] as f64, 
        b: bgcolour[2] as f64, 
        a: bgcolour[3] as f64,};

    // // // // // // // create command encoder
    let mut encoder = graphics.dev
        .create_command_encoder(&wgpu::CommandEncoderDescriptor {
            label: Some("Render Encoder"),
        });
    // // // // // // // setup render pass and buffers
    {
        let texture_view = graphics.tex.create_view(&Default::default());
        let texture_view_msaa = graphics.texaa.create_view(&Default::default());
        let render_pass_desc = wgpu::RenderPassDescriptor {
            label: Some("Render Pass"),
            color_attachments: &[wgpu::RenderPassColorAttachment {
                view: &texture_view_msaa,
                resolve_target: Some(&texture_view),
                ops: wgpu::Operations {
                    load: wgpu::LoadOp::Clear(bgcolour),
                    store: true,
                },
            }],
            depth_stencil_attachment: None,
        };

        let mut render_pass = encoder.begin_render_pass(&render_pass_desc);
        render_pass.set_pipeline(&graphics.rpl);
        render_pass.set_bind_group(0, &graphics.cbg, &[]);
        render_pass.set_vertex_buffer(0, vbff.slice(..));
        render_pass.draw(0..graphics.vbffsz, 0..1);
        
    }
    // // // // // // // setup output of render pass
    let u32_size = std::mem::size_of::<u32>() as u32;
    encoder.copy_texture_to_buffer(
        wgpu::ImageCopyTexture {
            aspect: wgpu::TextureAspect::All,
            texture: &graphics.tex,
            mip_level: 0,
            origin: wgpu::Origin3d::ZERO,
        },
        wgpu::ImageCopyBuffer {
            buffer: &graphics.obff,
            layout: wgpu::ImageDataLayout {
                offset: 0,
                bytes_per_row: NonZeroU32::new(u32_size * graphics.texsz),
                rows_per_image: NonZeroU32::new(graphics.texsz),
            },
        },
        graphics.texmemsz,
    );
    // // // // // // // send commands to the gpu

    let camera_uniform = CameraUniform {campos: [
        (tile[0] as f32 + 0.5)*TILESIZE , 
        (tile[1] as f32 + 0.5)*TILESIZE ,
        ]
    };

    graphics.que.write_buffer(&graphics.cbff, 0, bytemuck::cast_slice(&[camera_uniform]));

    graphics.que.submit(iter::once(encoder.finish()));
    let buffer_slice = graphics.obff.slice(..);

    // NOTE: We have to create the mapping THEN device.poll() before await
    // the future. Otherwise the application will freeze.
    let mapping = buffer_slice.map_async(wgpu::MapMode::Read);
    graphics.dev.poll(wgpu::Maintain::Wait);
    mapping.await.unwrap();
    // // // // // // save output to file
    {
        let data = buffer_slice.get_mapped_range();
        
        use image::{ImageBuffer, Rgba};
        let buffer =
        ImageBuffer::<Rgba<u8>, _>::from_raw(graphics.texsz, graphics.texsz, data).unwrap();
        buffer.save(fp).unwrap();
    }
    graphics.obff.unmap();
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

fn line2tris(line : &Line) -> [Vertex; 6]{
    
    let width = line.width;
    
    let to = Vertex {position: line.to, colour : line.colour};
    let from = Vertex {position: line.from, colour : line.colour};
    
    let normal: Vertex = normal(from, to);
    let ofset : Vertex = mul(normal,width/2.0);
    
    let v1 : Vertex = add(from, ofset);
    let v2 : Vertex = sub(from, ofset);
    
    let v3 : Vertex = add(to, ofset);
    let v4 : Vertex = sub(to, ofset);

    return [v1,v3,v2,v3,v4,v2];
}


fn ltorenderspace(line: &Line, tile: &[i32;2]) -> Line{
    let [tx,ty] = line.to;
    let [fx,fy] = line.from;
    let [xtilei,ytilei] = *tile;
    let xtile = xtilei as f32;
    let ytile = ytilei as f32;

    let t = [tx - (xtile+ 0.5)*TILESIZE, ty - (ytile+0.5)*TILESIZE ];
    let f = [fx - (xtile+ 0.5)*TILESIZE, fy - (ytile+0.5)*TILESIZE ];
    return Line{
        to : t,
        from : f,
        colour : line.colour,
        width : line.width,
    };
}

fn torenderspace(lines: &Vec<Line>, tile: &[i32;2]) -> Vec<Line> {
    let slines: Vec<Line> = lines
        .iter()
        .map(|line_ref| ltorenderspace(line_ref, tile))
        .collect();
    return slines;
}

pub fn make_draw_data(lines : &Vec<Line>) -> Vec::<Vertex>{
    
    let mut vertex_data = Vec::<Vertex>::new();
    
    let liter = lines.iter();
    
    for line in liter {
        let tris = line2tris(&line);
        vertex_data.extend(tris);
    }

    return vertex_data;
}



#[derive(Debug, Clone)]
pub struct Line{
    pub to : [f32;2],
    pub from : [f32;2],
    pub colour : [f32;3],
    pub width : f32,
}