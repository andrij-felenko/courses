pub struct GlvCurveConfig {
    inner: glv_curve_config_2d_t,
}

impl GlvCurveConfig {
    pub fn new(curve_name: &str) -> Result<Self, GlvError> {
        let mut config = std::mem::MaybeUninit::uninit();
        let c_name = std::ffi::CString::new(curve_name)?;
        unsafe {
            let status = glv_init_curve_2d(config.as_mut_ptr(), c_name.as_ptr());
            if status == 0 {
                Ok(Self { inner: config.assume_init() })
            } else {
                Err(GlvError::from_status(status))
            }
        }
    }
}
