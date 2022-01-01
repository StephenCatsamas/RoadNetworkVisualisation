use std::f32::consts::PI;
use std::collections::HashMap;
use crate::renderer::{Line,make_draw_data,setup,run};

const TILESIZE: f32 = 2.0;
const TEXSIZE: f32 = 512 as f32;

pub fn drawlineset(lines : Vec<Line>, view : View){
    let bgcolour = [0.1, 0.1, 0.1, 1.0];

    let lines = toscreenspace(lines, view);

    let tilehash = splitlines(lines);

    for (tile, lines) in &tilehash {
        let vert_dat = make_draw_data(lines, &tile);

        let graphics = pollster::block_on(setup(vert_dat, bgcolour));

        let fptile = format!("{:?}.png", tile);

        pollster::block_on(run(graphics, &fptile));
    }
}

fn project(line: &Line, view: &View) -> Line {
    let to = line.to;
    let from = line.from;
    let colour = line.colour;
    let width = line.width;

    let to = pix2scrn(deg2pix(to, view));
    let from = pix2scrn(deg2pix(from, view));

    return Line {
        to,
        from,
        colour,
        width,
    };
}

fn toscreenspace(lines: Vec<Line>, view: View) -> Vec<Line> {
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

    let xtile = ((x + (TILESIZE / 2.0)) / TILESIZE).floor() as i32;
    let ytile =((y + (TILESIZE / 2.0)) / TILESIZE).floor() as i32;
    
    let xpos = x - TILESIZE * (xtile as f32);
    let ypos = y - TILESIZE * (ytile as f32);

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

    return (xi <= x && x <= xf) && (yi <= y && y <= yf);
}

fn fmod(z : f32, m : f32) -> f32{
    (z%m + m)%m
}

fn quadrant(theta : f32) -> [f32;2]{
    return [(fmod(theta-0.5*PI,2.0*PI)-PI).signum(),
            theta.signum()]
}

fn gettiles(line: &Line) -> Vec<[i32; 2]> {
    let to = line.to;
    let [xo, yo] = to;
    let theta = lineangle(&line);
    let (s_tile, s_pos) = totile_pos(to);
    let [x, y] = s_pos;

    let [xdir,ydir] = quadrant(theta);

    let mut tiles = Vec::<[i32; 2]>::new();
    tiles.push(s_tile);

    let dx = 0.5 * TILESIZE - x;
    let xintdy = dx * theta.tan();
    //march for x intercepts
    let mut xm = xo + dx;
    let mut ym = yo + xintdy;

    while insegment([xm, ym], line) {
        xm += xdir*TILESIZE;
        ym += ydir*TILESIZE * theta.tan();
        let (tile, _pos) = totile_pos([xm + 0.5 * TILESIZE, ym]);
        tiles.push(tile);
    }

    let dy = 0.5 * TILESIZE - y;
    let yintdx = dy / theta.tan();
    //march for y intercepts
    let mut xm = xo + yintdx;
    let mut ym = yo + dy;

    while insegment([xm, ym], line) {
        let (tile, _pos) = totile_pos([xm, ym + 0.5 * TILESIZE]);
        tiles.push(tile);
        xm += xdir*TILESIZE / theta.tan();
        ym += ydir*TILESIZE;
    }

    return tiles;
}

fn splitlines(lines: Vec<Line>) -> HashMap<[i32; 2], Vec<Line>> {
    let mut tiles = HashMap::<[i32; 2], Vec<Line>>::new();

    for line in lines {
        let linetiles = gettiles(&line);
        for tile in linetiles {
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
    return tiles;
}