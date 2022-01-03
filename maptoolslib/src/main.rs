mod renderer;
mod draw;

use renderer::Line;
use draw::View;

fn main()  {

    let view = View { bounds: [-37.608,-37.94,145.173,144.72], res: 768.0 };
    let lines = draw::linesfromfile("seg.csv", 0.05);

    draw::drawlineset(lines, view, "rust_test\\");
}