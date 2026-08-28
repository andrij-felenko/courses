use std::os::raw::{c_char, c_int};
use std::ffi::CStr;

#[repr(C)]
pub struct BridgeConfig {
    pub sample_rate: i32,
    pub channels: i32,
    pub scale_factor: f64,
    pub enable_filter: u8,
    pub padding: [u8; 7],
}

enum BridgeContextOpaque {}

extern "C" {
    fn bridge_create_context(config: *const BridgeConfig, out_ctx: *mut *mut BridgeContextOpaque) -> c_int;
    fn bridge_process_buffer(
        ctx: *mut BridgeContextOpaque,
        input: *const f32,
        count: usize,
        out_buf: *mut *mut f32,
        out_count: *mut usize,
    ) -> c_int;
    fn bridge_free_buffer(buf: *mut f32);
    fn bridge_free_context(ctx: *mut BridgeContextOpaque);
    fn bridge_get_last_error(status: c_int) -> *const c_char;
}

pub struct NativeBridge {
    raw: *mut BridgeContextOpaque,
}

impl NativeBridge {
    pub fn new(sample_rate: i32, channels: i32, scale_factor: f64) -> Result<Self, String> {
        let config = BridgeConfig {
            sample_rate,
            channels,
            scale_factor,
            enable_filter: 1,
            padding: [0; 7],
        };
        let mut raw = std::ptr::null_mut();
        unsafe {
            let status = bridge_create_context(&config, &mut raw);
            if status != 0 {
                let err = CStr::from_ptr(bridge_get_last_error(status)).to_string_lossy().into_owned();
                return Err(err);
            }
            Ok(Self { raw })
        }
    }

    pub fn process(&self, data: &[f32]) -> Result<Vec<f32>, String> {
        let mut out_ptr = std::ptr::null_mut();
        let mut out_len = 0usize;

        unsafe {
            let status = bridge_process_buffer(self.raw, data.as_ptr(), data.len(), &mut out_ptr, &mut out_len);
            if status != 0 {
                let err = CStr::from_ptr(bridge_get_last_error(status)).to_string_lossy().into_owned();
                return Err(err);
            }

            let slice = std::slice::from_raw_parts(out_ptr, out_len);
            let result = slice.to_vec();
            bridge_free_buffer(out_ptr);
            Ok(result)
        }
    }
}

impl Drop for NativeBridge {
    fn drop(&mut self) {
        unsafe {
            if !self.raw.is_null() {
                bridge_free_context(self.raw);
            }
        }
    }
}
