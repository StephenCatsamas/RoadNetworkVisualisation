#[macro_use]
extern crate cpython;

use cpython::{Python, PyResult, PyObject, ObjectProtocol};
mod renderer;
use renderer::Line;
use std::collections::HashMap;

py_module_initializer!(maptoolslib, |py, m| {
    m.add(py, "__doc__", concat!("rust lib built at: ", include!(concat!(env!("OUT_DIR"), "/timestamp.txt"))))?;
    m.add(py, "rust_test", py_fn!(py, rust_test(a: PyObject)))?;
    m.add(py, "drawlines", py_fn!(py, drawlines(line: PyObject, view : PyObject, fp: &str)))?;
    Ok(())
});


fn rust_test(py: Python, a: PyObject) -> PyResult<u64> {
    println!("{}", a);
    
    let to = a.getattr(py, "to").unwrap();
    let tot = to.extract::<(f32,f32)>(py).unwrap();
    // let tp : (f32, f32) = tot.extract::<>(py).unwrap();
    print_type_of(&tot);
    println!("{}", tot.0);
    println!("{}", tot.1);
    
    Ok(7)
}

fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>())
}

fn array2<T>(tuple: (T,T)) -> [T;2] { 
    return [tuple.0,tuple.1];
 }
fn array3<T>(tuple: (T,T,T)) -> [T;3] { 
    return [tuple.0,tuple.1, tuple.2];
 }
fn array4<T>(tuple: (T,T,T,T)) -> [T;4] { 
    return [tuple.0,tuple.1, tuple.2, tuple.3];
 }



#[derive(Debug)]
struct View{
    bounds : [f32;4],
    res : f32,
}

impl View{
    fn frompy(py: Python, view: PyObject) -> View{           
        let b = array4(view.getattr(py, "bounds").unwrap()
                    .extract::<(f32,f32,f32,f32)>(py).unwrap());       
        let r = view.getattr(py, "res").unwrap()
                    .extract(py).unwrap();       
        let view = View{
            bounds : b,
            res : r
        };
        return view;    
    }
}

impl Line{
    fn frompy(py: Python, line: PyObject) -> Line{           
        let t = array2(line.getattr(py, "to").unwrap()
                    .extract::<(f32,f32)>(py).unwrap());        
        let f = array2(line.getattr(py, "fm").unwrap()
                    .extract::<(f32,f32)>(py).unwrap());        
        let c = array3(line.getattr(py, "colour").unwrap()
                    .extract::<(f32,f32,f32)>(py).unwrap());        
        let w = line.getattr(py, "width").unwrap()
                    .extract(py).unwrap();       
        let line = Line{
            to : t,
            from : f,
            colour : c,
            width : w,
        };
        return line;    
    }
}

fn linesfrompy(py: Python, lines: PyObject) -> Vec<Line> {
    let liter = lines.iter(py).unwrap();

    let mut lines = Vec::<Line>::new();

    for line in liter {
        let ln = Line::frompy(py,line.unwrap());
        lines.push(ln);
    }
    
    return lines; 

}

const TILESIZE:f32 = 2.0;

fn totile_pos(p : [f32;2]) -> ([u32;2],[f32;2]){
    let [x,y] = p;
    
    let xtile = (x + (TILESIZE / 2.0) % TILESIZE) as u32;
    let ytile = (y + (TILESIZE / 2.0) % TILESIZE) as u32;
    
    let xpos = x - TILESIZE*(xtile as f32);
    let ypos = y - TILESIZE*(ytile as f32);
    
    return ([xtile,ytile],[xpos,ypos]);

}

fn lineangle(line : &Line) -> f32 {
    let [x1,y1] = line.to;
    let [x2,y2] = line.from;
    
    let dx = x2-x1;
    let dy = y2-y1;
    
    return dy.atan2(dx);
    
}

fn insegment(p : [f32;2], line : &Line) -> bool{
    let [x1,y1] = line.to;
    let [x2,y2] = line.from;
    let [x,y] = p;
    
    let [xi,xf] = if x1 > x2 {[x2,x1]} else {[x1,x2]};
    let [yi,yf] = if y1 > y2 {[y2,y1]} else {[y1,y2]};
    
    return (xi <= x && x <= xf) && (yi <= y && y <= yf);
}

fn gettiles(line : &Line) -> Vec::<[u32;2]>{  
    let to = line.to;   
    let [xo,yo] = to;
    let theta = lineangle(&line);
    let (s_tile,s_pos) = totile_pos(to);
    let [x,y] = s_pos;

    let mut tiles = Vec::<[u32;2]>::new();
    tiles.push(s_tile);

    let dx = 0.5*TILESIZE - x;
    let xintdy = dx*theta.tan();
    //march for x intercepts
    let mut xm = xo + dx; 
    let mut ym = yo + xintdy; 
    
    while insegment([xm,ym],line){
        xm += TILESIZE; 
        ym += TILESIZE*theta.tan(); 
        let (tile,_pos) = totile_pos([xm+0.5*TILESIZE,ym]);
        tiles.push(tile);  
    }

    let dy = 0.5*TILESIZE - y;
    let yintdx = dy/theta.tan();
    //march for y intercepts
    let mut xm = xo + yintdx; 
    let mut ym = yo + dy; 
    
    while insegment([xm,ym],line){
        let (tile,_pos) = totile_pos([xm,ym+0.5*TILESIZE]);
        tiles.push(tile);  
        xm += TILESIZE/theta.tan(); 
        ym += TILESIZE; 
    }
    
    return tiles;
}

fn splitlines(lines : Vec<Line>) ->  HashMap<[u32;2],Vec<Line>>{
    let mut tiles =  HashMap::<[u32;2],Vec<Line>>::new();
    
    for line in lines{
        let linetiles = gettiles(&line);
        for tile in linetiles{
            match tiles.get_mut(&tile) {
                Some(v) => v.push(line.clone()),
                None => {
                            let mut v = Vec::<Line>::new();
                            v.push(line.clone());
                            tiles.insert(tile,v);                        
                        },
            }
        }
    }
    return tiles;
}

fn drawlines(py: Python, lines: PyObject, view : PyObject, fp: &str) -> PyResult<u64> {

    let bgcolour = [0.1,0.1,0.1,1.0];
    
    let view  = View::frompy(py,view);
    let lines = linesfrompy(py,lines);

    let lines = toscreenspace(lines, view);
    
    let line_sets = splitlines(lines);
    
    // let vert_dat = renderer::make_draw_data(lines);

    // let graphics = pollster::block_on(renderer::setup(vert_dat, bgcolour));

    // pollster::block_on(renderer::run(graphics, fp));
    
    return Ok(1);
    
}


fn project(line : &Line, view : &View) -> Line{
    let to = line.to;
    let from = line.from;
    let colour = line.colour;
    let width = line.width;
    
    let to = pix2scrn(deg2pix(to, view));
    let from = pix2scrn(deg2pix(from, view));

    return Line {to, from, colour, width};
}


fn toscreenspace(lines: Vec<Line>, view : View) -> Vec<Line>{
    let slines: Vec<Line> = lines.iter().map(|line_ref| project(line_ref, &view)).collect();
    return slines;
}

fn pix2scrn(pix : [f32;2]) -> [f32;2]{
    let tex_size = 512 as f32;
    
    let [x,y] = pix;
    
    let xs = 2.0*(x/tex_size) -1.0;
    let ys = 2.0*(-y/tex_size) +1.0;

    return [xs,ys];
}


//finds lat and lon from screen space pixel
fn pix2deg(pix : [f32;2], view : &View) -> [f32;2]{
    let [x,y] = pix;
    let [slat,_elat,_elon,slon] = view.bounds;
    let zl = 1.0/view.res;

        
    let lon = slon + x*zl;
    let lat = ifsecint((-y*zl).to_radians(),slat);
    return [lat,lon];
}    
//find screen space pixel from lat and lon
fn deg2pix(deg : [f32;2], view : &View) -> [f32;2]{
    let[lat,lon] = deg;
    let [slat,_elat,_elon,slon] = view.bounds;
    let zl = view.res;
  
    let y = (secint(lat, slat)).to_degrees() * zl;

    let x = (lon-slon) *zl;
    
    
    return [x,y]
}

fn sectan(z:f32) -> f32{
    let v = (1.0/z.cos()) + z.tan();
    return v;
}

//only for a,b in (-pi/2 to pi/2)
fn secint(a : f32,b : f32) -> f32{
    let a = a.to_radians();
    let b = b.to_radians();
    let up = sectan(b);
    let down = sectan(a);
    return up.ln() - down.ln();
}
//only for b in (-pi/2 to pi/2)
//find inverse for given initial point    
fn ifsecint(v : f32 ,a : f32) -> f32{
    let a = a.to_radians();

    let z = v.exp()*sectan(a);
    let b = ((z*z -1.0)/(1.0 + z*z)).asin();
    let b = b.to_degrees();
    return b;
}
//only for b in (-pi/2 to pi/2)
//find inverse for given end point    
fn iisecint(v : f32, b : f32) -> f32{
    let a = ifsecint(-v,b);
    return a;
}