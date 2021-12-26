#[macro_use]
extern crate glium;

use glium::{glutin, Surface};

fn main() {
    println!(concat!("rust bin built at: ", include!(concat!(env!("OUT_DIR"), "/timestamp.txt"))));
    
    glfunc();
    
}

#[derive(Copy, Clone, Debug)]
struct Vertex {
    position: [f32; 2],
}

fn glfunc(){
    println!("glfunc");
    
    
    
    let event_loop = glutin::event_loop::EventLoop::new();
    let size = glutin::dpi::LogicalSize {height: 400,width: 400};
    let wb = glutin::window::WindowBuilder::new().with_inner_size(size);
    let cb = glutin::ContextBuilder::new();
    let display = glium::Display::new(wb, cb, &event_loop).unwrap();

    implement_vertex!(Vertex, position);
    
    //triangle
    let from = Vertex { position: [0.5, 0.0] };
    let to = Vertex { position: [ 0.0,  0.5] };
    
    let  tris = line2tris(from,to ,0.1);
    println!("{:?}", tris);
    
    //send to vertex buffer
    let vertex_buffer = glium::VertexBuffer::new(&display, &tris).unwrap();
    
    //indicies
    let indices = glium::index::NoIndices(glium::index::PrimitiveType::TrianglesList);
    
    let vertex_shader_src = r#"
                                #version 140

                                in vec2 position;

                                void main() {
                                    gl_Position = vec4(position, 0.0, 1.0);
                                }
                            "#;
    
    let fragment_shader_src = r#"
                                #version 140

                                out vec4 color;

                                void main() {
                                    color = vec4(1.0, 0.0, 0.0, 1.0);
                                }
                            "#;
    
    let program = glium::Program::from_source(&display, vertex_shader_src, fragment_shader_src, None).unwrap();
    
    
    let mut target = display.draw();
    target.clear_color(0.0, 0.0, 1.0, 1.0);
        
    target.draw(&vertex_buffer, &indices, &program, &glium::uniforms::EmptyUniforms,
            &Default::default()).unwrap();
    
    target.finish().unwrap();
    
    // window_loop(event_loop);
    // println!("{}", event_loop)
    window_loop(event_loop);
    
}


fn window_loop(event_loop: glutin::event_loop::EventLoop<()>){

    event_loop.run(move |ev, _, control_flow| {
    let next_frame_time = std::time::Instant::now() +
        std::time::Duration::from_nanos(16_666_667);
    *control_flow = glutin::event_loop::ControlFlow::WaitUntil(next_frame_time);
    match ev {
        glutin::event::Event::WindowEvent { event, .. } => match event {
            glutin::event::WindowEvent::CloseRequested => {
                *control_flow = glutin::event_loop::ControlFlow::Exit;
                return;
            },
            _ => return,
        },
        _ => (),
    }
    });

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
    
   return Vertex {position: [x1 - x2, y1-y2]};
}

fn add(from : Vertex,to : Vertex) -> Vertex{
    let x1 : f32 = from.position[0];
    let y1 : f32 = from.position[1];
    
    let x2 : f32 = to.position[0];
    let y2 : f32 = to.position[1];
    
   return Vertex {position: [x1 + x2, y1+y2]};
}

fn mul(v : Vertex, s : f32) -> Vertex{
    let x : f32 = v.position[0];
    let y : f32 = v.position[1];
    
    return Vertex {position: [x*s, y*s]};
}

fn norm(v : Vertex) -> Vertex{
    let x : f32 = v.position[0];
    let y : f32 = v.position[1];

    let n : f32 = (x*x + y*y).sqrt();
    
    return Vertex {position: [x/n, y/n]};
    

}

fn normal(from : Vertex,to : Vertex) -> Vertex{
    
    let g : f32 = invgrad(from,to);
    
    let normal;
    if g != f32::MAX{
        normal = Vertex {position : [1.0, g]};
    }else{
        normal = Vertex {position : [0.0,1.0]};
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