// C++20 Gauss Verification Result Struct
namespace physics::electrodynamics {

struct GaussVerificationResult {
    double integrated_flux{0.0};
    double enclosed_charge{0.0};
    double theoretical_flux{0.0};
    double absolute_error{0.0};
    double relative_error_percent{0.0};
    size_t surface_cell_count{0};
};

} // namespace physics::electrodynamics
