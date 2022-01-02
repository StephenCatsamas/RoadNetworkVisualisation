use std::num::NonZeroU32;
use wgpu::util::DeviceExt;

#[repr(C)]
#[derive(Copy, Clone, Debug, bytemuck::Pod, bytemuck::Zeroable)]
pub struct Vertex {
    position: [f32; 2],
    colour: [f32; 3],
}

use crate::draw::{TILESIZE, TEXSIZE};


pub struct Graphics<'a>{
    device : wgpu::Device,   
    queue : wgpu::Queue,
    vbuff_layout : wgpu::VertexBufferLayout<'a>,
    tex_size : u32,
    tex_desc : Option<wgpu::TextureDescriptor<'a>>,
    texture : Option<wgpu::Texture>,
    render_pipeline : Option<wgpu::RenderPipeline>,
    output_buffer : Option<wgpu::Buffer>,
    encoder : Option<wgpu::CommandEncoder>,
}

fn make_vertex_buffer_layout() -> wgpu::VertexBufferLayout<'static>{
    let vbl = wgpu::VertexBufferLayout {
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
    return vbl;
}

fn draw(vert_dat: Vec::<Vertex>, graphics : &Graphics) -> (wgpu::Buffer, u32){
    let verticies = &vert_dat;

    let vertex_buffer = graphics.device.create_buffer_init(
        &wgpu::util::BufferInitDescriptor {
            label : Some("Vertex Buffer"),
            contents: bytemuck::cast_slice(verticies),
            usage: wgpu::BufferUsages::VERTEX,
        }
    );
    
    let size = verticies.len() as u32;
    
    return (vertex_buffer,size);
}

fn make_render_pipeline(graphics : &Graphics, texture_desc : &wgpu::TextureDescriptor) -> wgpu::RenderPipeline{
    let shader = graphics.device.create_shader_module(&wgpu::ShaderModuleDescriptor {
        label: Some("Vertex Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
    });

    let render_pipeline_layout = graphics.device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
        label: Some("Render Pipeline Layout"),
        bind_group_layouts: &[],
        push_constant_ranges: &[],
    });

    let render_pipeline = graphics.device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Render Pipeline"),
        layout: Some(&render_pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[graphics.vbuff_layout.clone()],
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
            // Requires Features::DEPTH_CLAMPING
            clamp_depth: false,
            // Requires Features::CONSERVATIVE_RASTERIZATION
            conservative: false,
        },
        depth_stencil: None,
        multisample: wgpu::MultisampleState {
            count: 4,
            mask: !0,
            alpha_to_coverage_enabled: true,
        },
    });
    
    return render_pipeline;
}

fn make_output_buffer(graphics : &Graphics) -> wgpu::Buffer{
    let u32_size = std::mem::size_of::<u32>() as u32;

    let output_buffer_size = (u32_size * graphics.tex_size * graphics.tex_size) as wgpu::BufferAddress;
    let output_buffer_desc = wgpu::BufferDescriptor {
        size: output_buffer_size,
        usage: wgpu::BufferUsages::COPY_DST
            // this tells wpgu that we want to read this buffer from the cpu
            | wgpu::BufferUsages::MAP_READ,
        label: None,
        mapped_at_creation: false,
    };
    
    return graphics.device.create_buffer(&output_buffer_desc)
}


fn make_texture_descriptor(graphics : &Graphics, samples:u32) -> wgpu::TextureDescriptor<'static>{
    let tex_size = graphics.tex_size;
    let tex_desc = wgpu::TextureDescriptor {
        size: wgpu::Extent3d {
            width: tex_size,
            height: tex_size,
            depth_or_array_layers: 1,
        },
        mip_level_count: 1,
        sample_count: samples,
        dimension: wgpu::TextureDimension::D2,
        format: wgpu::TextureFormat::Rgba8UnormSrgb,
        usage: wgpu::TextureUsages::COPY_SRC | wgpu::TextureUsages::RENDER_ATTACHMENT,
        label: None,
    };
    return tex_desc;
}

pub async fn setup(vert_dat : Vec::<Vertex>, bgcolour : [f32;4]) -> Graphics<'static>{
    
     let bgcolour = wgpu::Color {r: bgcolour[0] as f64, g: bgcolour[1] as f64, b: bgcolour[2] as f64, a: bgcolour[3] as f64,};
    
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

    let vertex_buffer_layout = make_vertex_buffer_layout();

    let mut graphics = Graphics {
        device : device,
        queue : queue,
        vbuff_layout : vertex_buffer_layout,
        tex_size : (TEXSIZE as u32), //must be a multiple of 64
        tex_desc : None,
        texture : None,
        render_pipeline : None,
        output_buffer : None,
        encoder : None,
    };
    

    let tex_desc_msaa = make_texture_descriptor(&graphics,4);
    graphics.tex_desc = Some(make_texture_descriptor(&graphics,1));
    graphics.texture = Some(graphics.device.create_texture(graphics.tex_desc.as_ref().unwrap()));
    let texture_msaa = graphics.device.create_texture(&tex_desc_msaa);
    graphics.output_buffer = Some(make_output_buffer(&graphics));
    graphics.render_pipeline = Some(make_render_pipeline(&graphics, graphics.tex_desc.as_ref().unwrap()));
    graphics.encoder = Some(graphics.device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: None }));

    let mut encoder = graphics.encoder.take().unwrap();
    
    {
        let texture_view = graphics.texture.as_ref().unwrap().create_view(&Default::default());
        let texture_view_msaa = texture_msaa.create_view(&Default::default());
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
        
        let vertex_buffer : wgpu::Buffer;
        let size : u32;
        
        let render_pipeline = graphics.render_pipeline.as_ref().unwrap();
        let mut render_pass = encoder.begin_render_pass(&render_pass_desc);

        render_pass.set_pipeline(&render_pipeline);
        
        let (t_vertex_buffer,t_size) = draw(vert_dat, &graphics);
        vertex_buffer = t_vertex_buffer;
        size = t_size;
        
        render_pass.set_vertex_buffer(0, vertex_buffer.slice(..));
        render_pass.draw(0..size, 0..1);
        
    }
    graphics.encoder = Some(encoder);
    return graphics;
}

pub async fn run(mut graphics : Graphics<'_>, fp : &str) {

    let output_buffer = graphics.output_buffer.take().unwrap();
    let mut encoder = graphics.encoder.take().unwrap();

    let texture = graphics.texture.as_ref().unwrap();

    let u32_size = std::mem::size_of::<u32>() as u32;
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
                bytes_per_row: NonZeroU32::new(u32_size * graphics.tex_size),
                rows_per_image: NonZeroU32::new(graphics.tex_size),
            },
        },
        graphics.tex_desc.as_ref().unwrap().size,
    );

    graphics.queue.submit(Some(encoder.finish()));
    
    let buffer_slice = output_buffer.slice(..);

    // NOTE: We have to create the mapping THEN device.poll() before await
    // the future. Otherwise the application will freeze.
    let mapping = buffer_slice.map_async(wgpu::MapMode::Read);
    graphics.device.poll(wgpu::Maintain::Wait);
    mapping.await.unwrap();
    

    save_buffer(&graphics, &buffer_slice, fp);
    
    
    output_buffer.unmap();
}

fn save_buffer(graphics : &Graphics, buffer_slice : &wgpu::BufferSlice, fp : &str ){
 
    let data = buffer_slice.get_mapped_range();

    use image::{ImageBuffer, Rgba};
    let buffer =
        ImageBuffer::<Rgba<u8>, _>::from_raw(graphics.tex_size, graphics.tex_size, data).unwrap();
    buffer.save(fp).unwrap();

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

pub fn make_draw_data(lines : &Vec<Line>, tile : &[i32;2]) -> Vec::<Vertex>{
    
    let mut vertex_data = Vec::<Vertex>::new();
    
    let rednderlines = torenderspace(lines, tile);

    let liter = rednderlines.iter();
    
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