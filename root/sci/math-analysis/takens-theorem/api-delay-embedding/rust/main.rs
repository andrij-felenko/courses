#[repr(C)]
pub struct TakensConfig {
    pub max_delay: usize,
    pub n_bins: usize,
    pub max_embedding_dim: usize,
    pub r_tol: f64,
    pub fnn_threshold: f64,
    pub num_threads: usize,
}

extern "C" {
    pub fn takens_config_init_default(config: *mut TakensConfig) -> i32;
    pub fn takens_compute_mutual_information(
        signal: *const f64,
        n: usize,
        config: *const TakensConfig,
        out_mi: *mut f64,
        out_opt_delay: *mut usize,
    ) -> i32;
}

pub struct TakensEmbedder<'a> {
    signal: &'a [f64],
    config: TakensConfig,
}

impl<'a> TakensEmbedder<'a> {
    pub fn new(signal: &'a [f64]) -> Self {
        let mut config = unsafe { std::mem::zeroed() };
        unsafe { takens_config_init_default(&mut config) };
        Self { signal, config }
    }

    pub fn compute_mutual_info(&self) -> Result<usize, i32> {
        let mut opt_delay: usize = 0;
        let res = unsafe {
            takens_compute_mutual_information(
                self.signal.as_ptr(),
                self.signal.len(),
                &self.config,
                std::ptr::null_mut(),
                &mut opt_delay,
            )
        };
        if res == 0 { Ok(opt_delay) } else { Err(res) }
    }
}
