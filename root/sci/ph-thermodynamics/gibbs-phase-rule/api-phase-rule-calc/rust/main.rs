use std::os::raw::{c_char, c_double, c_int};

#[repr(C)]
pub struct PhaseSystemSpecC {
    pub num_species: usize,
    pub num_reactions: usize,
    pub num_constraints: usize,
    pub num_phases: usize,
    pub is_condensed: bool,
    pub stoich_matrix_flat: *const c_double,
}

#[repr(C)]
pub struct PhaseResultSpecC {
    pub rank_reactions: usize,
    pub gibbs_components: usize,
    pub degrees_of_freedom: c_int,
    pub status_code: c_int,
    pub status_message: *const c_char,
}

extern "C" {
    pub fn thermo_analyze_phase_system(
        spec: *const PhaseSystemSpecC,
        result: *mut PhaseResultSpecC,
    ) -> c_int;
}
