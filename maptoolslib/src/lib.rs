#[macro_use]
extern crate cpython;

use cpython::{Python, PyResult};

fn rust_test(_py: Python, a: u64) -> PyResult<u64> {

    Ok(a)
}

py_module_initializer!(maptoolslib, |py, m| {
    m.add(py, "__doc__", concat!("rust lib built at: ", include!(concat!(env!("OUT_DIR"), "/timestamp.txt"))))?;
    m.add(py, "rust_test", py_fn!(py, rust_test(a: u64)))?;
    Ok(())
});
