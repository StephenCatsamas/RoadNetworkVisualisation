mod renderer;
mod draw;

use renderer::Line;
use draw::View;

fn main()  {

    let lines = draw::linesfromhex("seg.seg", 0.001);
    let view = View { bounds: [-37.608,-37.94,145.173,144.72], res: 4096.0 };

    //setup graphics.
    let mut graphics = pollster::block_on(renderer::setup());//9%

    draw::drawlineset(&mut graphics, lines, view, "rust_test\\");

}