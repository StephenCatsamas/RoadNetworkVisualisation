#[macro_use]
extern crate cpython;

use cpython::{ObjectProtocol, PyObject, PyResult, Python};

mod renderer;
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
        "drawlines",
        py_fn!(py, drawlines(line: PyObject, view: PyObject, fp: &str)),
    )?;
    Ok(())
});

fn rust_test(_py: Python, a: i32) -> PyResult<u64> {
    println!("{}", a);

    Ok(7)
}

fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>())
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


fn linesfrompy(py: Python, lines: PyObject) -> Vec<Line> {
    let liter = lines.iter(py).unwrap();

    let mut lines = Vec::<Line>::new();

    for line in liter {
        let ln = Line::frompy(py, line.unwrap());
        lines.push(ln);
    }

    return lines;
}



fn drawlines(py: Python, lines: PyObject, view: PyObject, fp: &str) -> PyResult<u64> {
    

    let view = View::frompy(py, view);
    let lines = linesfrompy(py, lines);

    draw::drawlineset(lines, view, fp);

    return Ok(1);
}

