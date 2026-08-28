// Приклад Rust FFI обгортки над engine_api.h
#[repr(C)]
#[derive(Copy, Clone, PartialEq, Debug)]
pub enum EngineStatus {
    Ok = 0,
    ErrInvalidArg = -1,
    ErrOutOfMemory = -2,
    ErrProcessing = -3,
    ErrUnknown = -4,
}

#[repr(C)]
pub struct EngineCtx {
    _private: [u8; 0], // Incomplete / Opaque type
}

extern "C" {
    pub fn engine_create(name: *const libc::c_char, out_ctx: *mut *mut EngineCtx) -> EngineStatus;
    pub fn engine_destroy(ctx: *mut EngineCtx);
    pub fn engine_process(
        ctx: *mut EngineCtx,
        input: *const u8,
        input_len: usize,
        output: *mut u8,
        inout_output_len: *mut usize,
    ) -> EngineStatus;
    pub fn engine_get_last_error() -> *const libc::c_char;
}

// Безпечна RAII обгортка в Rust
pub struct SafeEngine {
    raw: *mut EngineCtx,
}

impl SafeEngine {
    pub fn new(algo: &str) -> Result<Self, String> {
        let c_algo = std::ffi::CString::new(algo).unwrap();
        let mut raw = std::ptr::null_mut();
        unsafe {
            let status = engine_create(c_algo.as_ptr(), &mut raw);
            if status != EngineStatus::Ok {
                let err_ptr = engine_get_last_error();
                let err_str = std::ffi::CStr::from_ptr(err_ptr).to_string_lossy().into_owned();
                return Err(err_str);
            }
            Ok(SafeEngine { raw })
        }
    }
}

impl Drop for SafeEngine {
    fn drop(&mut self) {
        unsafe {
            engine_destroy(self.raw);
        }
    }
}
