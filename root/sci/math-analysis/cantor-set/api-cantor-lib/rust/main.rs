use std::os::raw::{c_double, c_int, c_void};

#[repr(C)]
pub struct CantorInterval {
    pub start: c_double,
    pub end: c_double,
}

extern "C" {
    pub fn cantor_contains(x: c_double, max_depth: c_int, result: *mut bool) -> i32;
    pub fn cantor_generate_level(level: c_int) -> *mut c_void;
}

pub fn is_in_cantor_set(x: f64, max_depth: i32) -> bool {
    let mut res = false;
    unsafe {
        cantor_contains(x, max_depth, &mut res);
    }
    res
}
