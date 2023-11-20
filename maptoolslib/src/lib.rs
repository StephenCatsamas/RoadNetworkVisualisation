use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use std::time::Instant;

mod draw;
mod renderer;
mod seg;

use draw::View;
use renderer::Graphics;

static mut GRAPHICS: Option<Graphics> = None;

#[pyfunction]
fn rust_test(_py: Python, a: i32) -> PyResult<u64> {
    println!("{}", a);

    Ok(7)
}

fn array2<T>(tuple: (T, T)) -> [T; 2] {
    return [tuple.0, tuple.1];
}
fn array3<T>(tuple: (T, T, T)) -> [T; 3] {
    return [tuple.0, tuple.1, tuple.2];
}
fn array4<T>(tuple: (T, T, T, T)) -> [T; 4] {
    return [tuple.0, tuple.1, tuple.2, tuple.3];
}

impl View {
    fn frompy(py: Python, view: PyObject) -> View {
        let b = array4(
            view.getattr(py, "bounds")
                .unwrap()
                .extract::<(f32, f32, f32, f32)>(py)
                .unwrap(),
        );
        let r = view.getattr(py, "res").unwrap().extract(py).unwrap();
        let view = View { bounds: b, res: r };
        return view;
    }
}

#[pyfunction]
fn graphics_init(py: Python) -> PyResult<u64> {
    unsafe {
        let tik = Instant::now();
        if GRAPHICS.is_none() {
            GRAPHICS = Some(pollster::block_on(renderer::setup()));
        }
        println!("initialised graphics: {}", tik.elapsed().as_millis());
    }
    return Ok(0);
}

#[pyfunction]
fn drawfile(py: Python, fin: &str, view: PyObject, fout: &str, width: f32) -> PyResult<u64> {
    let view = View::frompy(py, view);
    let lines = draw::linesfromhex(fin, width);

    unsafe {
        let mut graphics = GRAPHICS
            .take()
            .ok_or_else(|| PyValueError::new_err("GRAPHICS is None"))?;
        draw::drawlineset(&mut graphics, lines, view, fout);
        GRAPHICS = Some(graphics);
    }
    return Ok(0);
}

#[pyfunction]
fn segfile(py: Python, fin: &str, fout: &str) -> PyResult<u64> {
    let segments = seg::load_map(fin);
    let lines = seg::format(segments);
    seg::tofile(fout, lines);

    return Ok(0);
}

#[pymodule]
fn maptoolslib(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_test, m)?)?;
    m.add_function(wrap_pyfunction!(graphics_init, m)?)?;
    m.add_function(wrap_pyfunction!(segfile, m)?)?;
    m.add_function(wrap_pyfunction!(drawfile, m)?)?;
    Ok(())
}
