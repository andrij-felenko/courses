namespace baroclinic {

class BaroclinicException : public std::runtime_error {
public:
    explicit BaroclinicException(int code)
        : std::runtime_error(std::string(get_error_string(code))), code_(code) {}
    int code() const noexcept { return code_; }
private:
    int code_;
};

class Solver {
public:
    explicit Solver(BaroclinicGridConfig config) : config_(config) {
        init_config(config_);
    }

    // Обчислення моменту завихреності через std::span (без копіювання)
    std::vector<double> compute_torque(
        std::span<const double> pressure,
        std::span<const double> density) const
    {
        const size_t total = config_.nx * config_.ny * config_.nz;
        if (pressure.size() != total || density.size() != total) {
            throw BaroclinicException(BAROCLINIC_ERR_OUT_OF_BOUNDS);
        }

        std::vector<double> torque(total, 0.0);
        BaroclinicState state{.pressure = pressure, .density = density};
        BaroclinicOutput out{.baroclinic_torque_z = torque};

        int rc = compute_torque(config_, state, out);
        if (rc < 0) throw BaroclinicException(rc);

        return torque;
    }

    const BaroclinicGridConfig& config() const noexcept { return config_; }

private:
    BaroclinicGridConfig config_;
};

} // namespace baroclinic
