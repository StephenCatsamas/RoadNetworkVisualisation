use pyo3::prelude::*;

mod renderer;
mod seg;
mod draw;

use draw::View;

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
fn drawfile(py: Python, file : &str, view: PyObject, fp: &str, width : f32) -> PyResult<u64> {
    
    let view = View::frompy(py, view);
    let lines = draw::linesfromhex(file, width);
    let mut graphics = pollster::block_on(renderer::setup());

    draw::drawlineset(&mut graphics, lines, view, fp);

    return Ok(1);
}

#[pyfunction]
fn segfile(py: Python, fin: &str, fout: &str) -> PyResult<u64> {
    
    let segments = seg::load_map(fin);
    let lines = seg::format(segments);
    seg::tofile(fout, lines);

    return Ok(1);
}



#[pymodule]
fn maptoolslib(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_test, m)?)?;
    m.add_function(wrap_pyfunction!(segfile, m)?)?;
    m.add_function(wrap_pyfunction!(drawfile, m)?)?;
    Ok(())
}
