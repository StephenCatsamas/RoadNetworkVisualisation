mod renderer;
mod draw;

use renderer::Line;
use draw::View;

fn main()  {

    let lines = draw::linesfromhex("seg.seg", 0.001);
    
    for _i in 0..20{
        let view = View { bounds: [-37.608,-37.94,145.173,144.72], res: 4096.0 };
        draw::drawlineset(lines.clone(), view, "rust_test\\");
    }
}