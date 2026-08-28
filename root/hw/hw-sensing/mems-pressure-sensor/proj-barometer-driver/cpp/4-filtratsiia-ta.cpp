namespace drivers {

class AltimeterFilter {
private:
    double filtered_pressure_pa_{101325.0};
    double alpha_{0.15};
    double qnh_pa_{101325.0};
    bool initialized_{false};

public:
    constexpr explicit AltimeterFilter(double alpha = 0.15, double qnh_pa = 101325.0) noexcept
        : alpha_(alpha), qnh_pa_(qnh_pa) {}

    void set_qnh(double qnh_pa) noexcept {
        qnh_pa_ = qnh_pa;
    }

    [[nodiscard]] BaroSample process(double raw_pressure_pa, double temperature_c) noexcept {
        if (!initialized_) {
            filtered_pressure_pa_ = raw_pressure_pa;
            initialized_ = true;
        } else {
            filtered_pressure_pa_ += alpha_ * (raw_pressure_pa - filtered_pressure_pa_);
        }

        const double p_ratio = filtered_pressure_pa_ / qnh_pa_;
        const double altitude = 44330.77 * (1.0 - std::pow(p_ratio, 0.190263));

        return BaroSample{
            .pressure_pa = filtered_pressure_pa_,
            .temperature_c = temperature_c,
            .altitude_m = altitude
        };
    }

    void reset() noexcept {
        initialized_ = false;
    }
};

} // namespace drivers
