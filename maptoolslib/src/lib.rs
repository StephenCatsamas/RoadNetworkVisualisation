#[macro_use]
extern crate cpython;

use cpython::{ObjectProtocol, PyObject, PyResult, Python};

mod renderer;
mod seg;
mod draw;

use renderer::Line;
use draw::View;

py_module_initializer!(maptoolslib, |py, m| {
    m.add(
        py,
        "__doc__",
        concat!(
            "rust lib built at: ",
            include!(concat!(env!("OUT_DIR"), "/timestamp.txt"))
        ),
    )?;
    m.add(py, "rust_test", py_fn!(py, rust_test(a: i32)))?;
    m.add(
        py,
        "segfile",
        py_fn!(py, segfile(fin: &str, fout: &str)),
    )?;
    m.add(
        py,
        "drawfile",
        py_fn!(py, drawfile(file: &str, view: PyObject, fp: &str, width : f32)),
    )?;
    Ok(())
});

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

impl Line {
    fn frompy(py: Python, line: PyObject) -> Line {
        let t = array2(
            line.getattr(py, "to")
                .unwrap()
                .extract::<(f32, f32)>(py)
                .unwrap(),
        );
        let f = array2(
            line.getattr(py, "fm")
                .unwrap()
                .extract::<(f32, f32)>(py)
                .unwrap(),
        );
        let c = array3(
            line.getattr(py, "colour")
                .unwrap()
                .extract::<(f32, f32, f32)>(py)
                .unwrap(),
        );
        let w = line.getattr(py, "width").unwrap().extract(py).unwrap();
        let line = Line {
            to: t,
            from: f,
            colour: c,
            width: w,
        };
        return line;
    }
}


fn drawfile(py: Python, file : &str, view: PyObject, fp: &str, width : f32) -> PyResult<u64> {
    
    let view = View::frompy(py, view);
    let lines = draw::linesfromhex(file, width);
    let mut graphics = pollster::block_on(renderer::setup());

    draw::drawlineset(&mut graphics, lines, view, fp);

    return Ok(1);
}

fn segfile(py: Python, fin: &str, fout: &str) -> PyResult<u64> {
    
    let segments = seg::load_map(fin);
    let lines = seg::format(segments);
    seg::tofile(fout, lines);

    return Ok(1);
}

