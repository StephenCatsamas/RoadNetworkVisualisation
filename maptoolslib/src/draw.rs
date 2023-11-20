use std::f32::consts::PI;
use std::collections::HashMap;
use crate::renderer::{self, Line, Graphics};

use std::fs::{self, File};
use std::io::{self, BufRead};


pub const TILESIZE: f32 = 2.0;
pub const TEXSIZE: f32 = 512 as f32;
const F32MRG : f32 = 1E-6;
const BINARY_LINE_SIZE : usize = (2+2+3)*4;//(to,from,colour) in f32s.

pub fn drawlineset(graphics : &mut Graphics, lines : Vec<Line>, view : View, fp : &str){
    let bgcolour = [0.05, 0.05, 0.05, 1.0];

    let lines = toscreenspace(lines, &view);

    let vert_dat = renderer::make_draw_data(&lines);

    renderer::setvertdata(graphics, &vert_dat);
    
    let rendertiles = view2tiles(&view);
    for tile in rendertiles {
        let fptile = format!("{}{:?}.tiff", fp, tile);
        pollster::block_on(renderer::run(graphics, tile, bgcolour, &fptile));//4%
    }
}


#[allow(non_snake_case)]
fn view2tiles(view : &View) -> Vec<[i32;2]>{
    let [Nv,Sv,Ev,Wv] = view.bounds;
    
    let (NWtile, _pos) = totile_pos(pix2scrn(deg2pix([Nv, Wv],&view)));
    let (SEtile, _pos) = totile_pos(pix2scrn(deg2pix([Sv, Ev],&view)));

    let mut rendertiles = Vec::<[i32;2]>::new();

    for x in NWtile[0]..(SEtile[0]+1){//take noteness of endpoint inclusions
    for y in SEtile[1]..NWtile[1]{
        rendertiles.push([x,y]);
    }
    }
    return rendertiles;
}


fn btof32 (bref : &[u8]) -> f32{
    const F32SIZE : usize = std::mem::size_of::<f32>();
    let barr : [u8; F32SIZE] = bref.try_into().unwrap();
    f32::from_ne_bytes(barr)
}

//use ittertools chunks to group binary data
pub fn linesfromhex(fp : &str, width : f32) -> Vec<Line>{
    const F32SIZE : usize = std::mem::size_of::<f32>();
    let mut lvec = Vec::<Line>::new();

    
    let data = fs::read(fp).unwrap();
        let lineiter = data.chunks_exact(BINARY_LINE_SIZE);
        if lineiter.remainder().len() != 0 {
            println!("WARN:: Unexpected data at end of segment file");
        }
        for binline in lineiter{
            let mut to : [f32;2] = [f32::NAN; 2];
            let mut from : [f32;2] = [f32::NAN; 2];
            let mut colour : [f32;3] = [f32::NAN; 3];

            for (field, bfltdat) in binline.chunks(F32SIZE).enumerate(){
                match field{
                    0 => {to[0] = btof32(bfltdat);}
                    1 => {to[1] = btof32(bfltdat);}
                    2 => {from[0] = btof32(bfltdat);}
                    3 => {from[1] = btof32(bfltdat);}
                    4 => {colour[0] = btof32(bfltdat);}
                    5 => {colour[1] = btof32(bfltdat);}
                    6 => {colour[2] = btof32(bfltdat);}
                    _ => {},
                }
            }
            let l = Line{
                to,
                from,
                colour,
                width : width,
            };
            lvec.push(l);         
        }
    
    return lvec;
}

#[allow(dead_code)]
pub fn linesfromascii(fp : &str, width : f32) -> Vec<Line>{
    let mut lvec = Vec::<Line>::new();

    let mut to : Option<[f32;2]> = None;
    let mut from : Option<[f32;2]> = None;
    let mut colour : Option<[f32;3]> = None;
    if let Ok(lines) = read_lines(fp) {
        for line in lines {
            if let Ok(ip) = line {
                let fields = ip.split(';');
                for (pos,feild) in fields.enumerate(){
                    match pos{
                        0 => {
                            let rawtup = feild.replace(&['(',')',' '][..], "");
                            let entries = rawtup.split(',');
                            to = Some(entries.map(|v| v.parse::<f32>().unwrap())
                                                .collect::<Vec<f32>>()
                                                .try_into()
                                                .unwrap());
                        },
                        1 => {
                            let rawtup = feild.replace(&['(',')',' '][..], "");
                            let entries = rawtup.split(',');
                            from = Some(entries.map(|v| v.parse::<f32>().unwrap())
                                                .collect::<Vec<f32>>()
                                                .try_into()
                                                .unwrap());
                        },
                        2 => {
                            let rawtup = feild.replace(&['(',')',' '][..], "");
                            let entries = rawtup.split(',');
                            colour = Some(entries.map(|v| v.parse::<f32>().unwrap())
                                                .collect::<Vec<f32>>()
                                                .try_into()
                                                .unwrap());
                        },
                        _ => {},
                    }
                }
                let l = Line{
                    to : to.take().unwrap(),
                    from : from.take().unwrap(),
                    colour : colour.take().unwrap(),
                    width : width,
                };
                lvec.push(l);

            }          
        }
    }
    return lvec;
}

fn read_lines(filename: &str) -> io::Result<io::Lines<io::BufReader<File>>> {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn project(line: &Line, view: &View) -> Line {
    let to = line.to;
    let from = line.from;
    let colour = line.colour;
    let width = line.width;

    let tpix = deg2pix(to, view);
    let to = pix2scrn(tpix);
    let fpix = deg2pix(from, view);
    let from = pix2scrn(fpix);

    return Line {
        to,
        from,
        colour,
        width,
    };
}

fn toscreenspace(lines: Vec<Line>, view: &View) -> Vec<Line> {
    let slines: Vec<Line> = lines
        .iter()
        .map(|line_ref| project(line_ref, &view))
        .collect();
    return slines;
}

fn pix2scrn(pix: [f32; 2]) -> [f32; 2] {
    let [x, y] = pix;

    let xs = TILESIZE * (x / TEXSIZE);
    let ys = TILESIZE * (-y / TEXSIZE);

    return [xs, ys];
}

//finds lat and lon from screen space pixel
fn pix2deg(pix: [f32; 2], view: &View) -> [f32; 2] {
    let [x, y] = pix;
    let [slat, _elat, _elon, slon] = view.bounds;
    let zl = 1.0 / view.res;

    let lon = slon + x * zl;
    let lat = ifsecint((-y * zl).to_radians(), slat);
    return [lat, lon];
}
//find screen space pixel from lat and lon
fn deg2pix(deg: [f32; 2], view: &View) -> [f32; 2] {
    let [lat, lon] = deg;
    let [slat, _elat, _elon, slon] = view.bounds;
    let zl = view.res;

    let y = (secint(lat, slat)).to_degrees() * zl;

    let x = (lon - slon) * zl;

    return [x, y];
}

fn sectan(z: f32) -> f32 {
    let v = (1.0 / z.cos()) + z.tan();
    return v;
}

//only for a,b in (-pi/2 to pi/2)
fn secint(a: f32, b: f32) -> f32 {
    let a = a.to_radians();
    let b = b.to_radians();
    let up = sectan(b);
    let down = sectan(a);
    return up.ln() - down.ln();
}
//only for b in (-pi/2 to pi/2)
//find inverse for given initial point
fn ifsecint(v: f32, a: f32) -> f32 {
    let a = a.to_radians();

    let z = v.exp() * sectan(a);
    let b = ((z * z - 1.0) / (1.0 + z * z)).asin();
    let b = b.to_degrees();
    return b;
}
//only for b in (-pi/2 to pi/2)
//find inverse for given end point
fn iisecint(v: f32, b: f32) -> f32 {
    let a = ifsecint(-v, b);
    return a;
}

#[derive(Debug)]
pub struct View {
    pub bounds: [f32; 4],
    pub res: f32,
}

fn totile_pos(p: [f32; 2]) -> ([i32; 2], [f32; 2]) {
    let [x, y] = p;

    let xtile = (x / TILESIZE).floor() as i32;
    let ytile = (y / TILESIZE).floor() as i32;
    
    let xpos = fmod(x,TILESIZE);
    let ypos = fmod(y, TILESIZE);

    return ([xtile, ytile], [xpos, ypos]);
}

fn lineangle(line: &Line) -> f32 {
    let [x1, y1] = line.to;
    let [x2, y2] = line.from;

    let dx = x2 - x1;
    let dy = y2 - y1;

    return dy.atan2(dx);
}

fn insegment(p: [f32; 2], line: &Line) -> bool {
    let [x1, y1] = line.to;
    let [x2, y2] = line.from;
    let [x, y] = p;

    let [xi, xf] = if x1 > x2 { [x2, x1] } else { [x1, x2] };
    let [yi, yf] = if y1 > y2 { [y2, y1] } else { [y1, y2] };

    return (xi - F32MRG  <= x && x <= xf + F32MRG ) && (yi - F32MRG <= y && y <= yf + F32MRG);
}

fn fmod(z : f32, m : f32) -> f32{
    (z%m + m)%m
}

fn quadrant(theta : f32) -> [f32;2]{
    return [(fmod(theta-0.5*PI,2.0*PI)-PI).signum(),
            theta.signum()]
}

enum InterceptType {
    X,
    Y,
    XY,
    None,
}

fn near1(z : f32) -> bool{
    if (z-1.0).abs() < F32MRG {true} else {false}
}

fn find_intr_type([x,y] : [f32;2]) -> InterceptType {
     let [rx,ry] = [fmod(x+1.0, TILESIZE), fmod(y+1.0, TILESIZE)];

    if near1(rx) && near1(ry) {return InterceptType::XY};
    if near1(rx) {return InterceptType::Y};
    if near1(ry) {return InterceptType::X};
    return InterceptType::None;

}

//may return same tile more than once
fn gettiles(line: &Line) -> Vec<[i32; 2]> {
    let to = line.to;
    let [xo, yo] = to;
    let theta = lineangle(&line);
    let (s_tile, s_pos) = totile_pos(to);
    let [x, y] = s_pos;

    let [xdir,ydir] = quadrant(theta);

    let mut tiles = Vec::<[i32; 2]>::new();
    tiles.push(s_tile);


    //find first intercepts along the segment
    let xintdy = if ydir == 1.0 {TILESIZE - y} else {-y};
    let xintdx = xintdy / theta.tan();

    let yintdx = if xdir == 1.0 {TILESIZE - x} else {-x};
    let yintdy = yintdx * theta.tan();

    let mut xint_xn = xo + xintdx;
    let mut xint_yn = yo + xintdy;

    let mut yint_xn = xo + yintdx;
    let mut yint_yn = yo + yintdy;

    //march to first intercepts
    let mut xm = if (xintdy-yo).abs() < (yintdy-yo).abs() {xint_xn} else {yint_xn};
    let mut ym = if (xintdy-yo).abs() < (yintdy-yo).abs() {xint_yn} else {yint_yn};

    while insegment([xm,ym], line){
        
        match find_intr_type([xm,ym]){
            InterceptType::X => {
                let (tile, _pos) = totile_pos([xm , ym + 0.5*TILESIZE*ydir]);
                tiles.push(tile);

                xint_xn = xm + xdir*TILESIZE / theta.tan();
                xint_yn = ym + ydir*TILESIZE;
            },
            InterceptType::Y => {
                let (tile, _pos) = totile_pos([xm + 0.5*TILESIZE*xdir, ym ]);
                tiles.push(tile);

                yint_xn = xm + xdir*TILESIZE;
                yint_yn = ym + ydir*TILESIZE * theta.tan();
            },
            InterceptType::XY => {//on corners we need to do every tile except the one we came from
                for [dx,dy] in [[1.0,1.0],[1.0,-1.0],[-1.0,1.0]]{//only when dy,dx == 1 are we going in the direction we came from
                    let (tile, _pos) = totile_pos([xm + 0.5*TILESIZE*xdir*dx, ym + 0.5*TILESIZE*ydir*dy]);
                    tiles.push(tile);
                }
            
                xint_xn = xm + xdir*TILESIZE;
                xint_yn = ym + ydir*TILESIZE*theta.tan();
                yint_xn = xm + xdir*TILESIZE/theta.tan();
                yint_yn = ym + ydir*TILESIZE;
            },
            InterceptType::None => {
                panic!();
            },
        }

        //do marching
        xm = if (xint_yn-yo).abs() < (yint_yn-yo).abs() {xint_xn} else {yint_xn};
        ym = if (xint_yn-yo).abs() < (yint_yn-yo).abs() {xint_yn} else {yint_yn};

    }
    return tiles;
}

#[allow(dead_code)]
//splits lines into where they are visible from
fn splitlines(lines: Vec<Line>, view : &View) -> HashMap<[i32; 2], Vec<Line>> {
    let mut tiles = HashMap::<[i32; 2], Vec<Line>>::new();

    for line in lines {
        let linetiles = gettiles(&line);
        for tile in linetiles {
            if !in_view(tile, &view) {continue}
            match tiles.get_mut(&tile) {
                Some(v) => v.push(line.clone()),
                None => {
                    let mut v = Vec::<Line>::new();
                    v.push(line.clone());
                    tiles.insert(tile, v);
                }
            }
        }
    }
    complete_rect(&mut tiles);


    return tiles;
}

fn complete_rect(tiles: &mut HashMap<[i32; 2], Vec<Line>>) {
    let xsize = tiles.keys().map(|cords| cords[0]).max().unwrap();
    let ysize = tiles.keys().map(|cords| cords[1]).min().unwrap();

    for x in 0..xsize{
    for y in ysize..-1{
        let tile = [x,y];
        match tiles.get_mut(&tile) {
            Some(_v) => {},
            None => {
                let v = Vec::<Line>::new();
                tiles.insert(tile, v);
            }
        }
    }
    }

}

#[allow(non_snake_case)]
fn in_view(tile : [i32;2], view : &View) -> bool{
    let [Nv,Sv,Ev,Wv] = view.bounds;
    
    let (NWtile, _pos) = totile_pos(pix2scrn(deg2pix([Nv, Wv],&view)));
    let (SEtile, _pos) = totile_pos(pix2scrn(deg2pix([Sv, Ev],&view)));

    return (NWtile[0] <= tile[0] && tile[0] <= SEtile[0])//westness 
    && (SEtile[1] <= tile[1] && tile[1] < NWtile[1])//northness//take note of inequality strictness
}