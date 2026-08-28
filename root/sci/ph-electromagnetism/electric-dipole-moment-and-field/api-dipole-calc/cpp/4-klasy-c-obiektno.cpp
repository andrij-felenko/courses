namespace physics::electromagnetism {

class ElectricDipole {
public:
    constexpr ElectricDipole() noexcept = default;
    constexpr ElectricDipole(const dipole_vec3_t& pos, const dipole_vec3_t& mom) noexcept
        : position_(pos), moment_(mom) {}

    [[nodiscard]] static ElectricDipole from_debye(const dipole_vec3_t& pos, 
                                                   const dipole_vec3_t& mom_dir, 
                                                   double debye_val) noexcept {
        const double factor = debye_val * 3.33564e-30;
        return ElectricDipole{pos, {mom_dir.x * factor, mom_dir.y * factor, mom_dir.z * factor}};
    }

    [[nodiscard]] const dipole_vec3_t& position() const noexcept { return position_; }
    [[nodiscard]] const dipole_vec3_t& moment() const noexcept { return moment_; }

    [[nodiscard]] dipole_field_result_t calculate_field(const dipole_vec3_t& obs_point, 
                                                         double cutoff = 1e-12) const noexcept {
        dipole_field_result_t res{};
        electric_dipole_t raw{position_, moment_, 0.0};
        dipole_calc_field(&raw, &obs_point, cutoff, &res);
        return res;
    }

private:
    dipole_vec3_t position_{0.0, 0.0, 0.0};
    dipole_vec3_t moment_{0.0, 0.0, 0.0};
};

} // namespace physics::electromagnetism
