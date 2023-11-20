mod draw;
mod renderer;
mod seg;

use draw::View;
use std::time::Instant;

fn main() {
    // let mut tik = Instant::now();
    // let segemnts = seg::load_map("map.osm");
    // let lines = seg::format(segemnts);
    // seg::tofile("segout.seg", lines);
    // println!("t0: {}", tik.elapsed().as_millis());
    render_test();
}



#[allow(dead_code)]
fn render_test() {
    let mut tik = Instant::now();

    let lines = draw::linesfromhex("segout.seg", 0.001);
    let view = View {
        bounds: [-37.608, -37.94, 145.173, 144.72],
        res: 4096.0,
    };

    println!("t0: {}", tik.elapsed().as_millis());
    tik = Instant::now();

    //setup graphics.
    let mut graphics = pollster::block_on(renderer::setup()); //9%

    println!("t1: {}", tik.elapsed().as_millis());
    tik = Instant::now();

    draw::drawlineset(&mut graphics, lines, view, "rust_test\\");

    println!("t2: {}", tik.elapsed().as_millis());
    // tik = Instant::now();
}
