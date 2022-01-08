mod renderer;
mod draw;

use draw::View;
use std::time::{Instant};

fn main()  {
   

}


pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// This is a really bad adding function, its purpose is to fail in this
// example.
#[allow(dead_code)]
fn bad_add(a: i32, b: i32) -> i32 {
    a - b
}

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(1, 2), 3);
    }

    #[test]
    fn test_bad_add() {
        // This assert would fire and test will fail.
        // Please note, that private functions can be tested too!
        assert_eq!(bad_add(1, 2), 3);
    }
}

#[allow(dead_code)]
fn render_test() {
    let mut tik = Instant::now();

    let lines = draw::linesfromhex("seg.seg", 0.001);
    let view = View { bounds: [-37.608,-37.94,145.173,144.72], res: 4096.0 };

    println!("t0: {}", tik.elapsed().as_millis());
    tik = Instant::now();

    //setup graphics.
    let mut graphics = pollster::block_on(renderer::setup());//9%

    println!("t1: {}", tik.elapsed().as_millis());
    tik = Instant::now();

    draw::drawlineset(&mut graphics, lines, view, "rust_test\\");

    println!("t2: {}", tik.elapsed().as_millis());
    // tik = Instant::now();
}