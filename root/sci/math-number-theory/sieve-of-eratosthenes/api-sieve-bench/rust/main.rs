#[repr(C)]
pub struct SieveConfig {
    pub start_n: u64,
    pub end_n: u64,
    pub segment_size: u32,
    pub thread_count: u32,
    pub wheel: i32,
    pub count_only: bool,
}

extern "C" {
    pub fn sieve_execute(config: *const SieveConfig, result: *mut SieveResult) -> i32;
    pub fn sieve_free_result(result: *mut SieveResult);
}
