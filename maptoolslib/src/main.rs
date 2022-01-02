mod renderer;
mod draw;

use renderer::Line;
use draw::View;

fn main()  {

    let mut lines = Vec::<Line>::new();

    let l1 = Line{
        to : [1.0,1.0],
        from : [1.0,-1.0],
        colour : [1.0,1.0,1.0],
        width : 0.1,
    };
    lines.push(l1);

    let view = View { bounds: [1.0,-1.0,1.0,-1.0], res: 768.0 };

    draw::drawlineset(lines, view);
}