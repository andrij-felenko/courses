// Ідіоматичний C++ constexpr калькулятор компенсації
namespace drivers {

struct CalibratedData {
    double pressure_pa;
    double temperature_c;
};

[[nodiscard]] constexpr CalibratedData compensate(uint32_t raw_p, uint32_t raw_t, const BaroCalibCoeffs& c) noexcept {
    const double dt = static_cast<double>(raw_t) - c.t1;
    const double t_lin = (dt * c.t2) + (dt * dt * c.t3);

    const double t2 = t_lin * t_lin;
    const double t3 = t2 * t_lin;
    const double p_raw = static_cast<double>(raw_p);
    const double p2 = p_raw * p_raw;
    const double p3 = p2 * p_raw;

    const double offset = c.p1 + (c.p2 * t_lin) + (c.p3 * t2) + (c.p4 * t3);
    const double sens   = c.p5 + (c.p6 * t_lin) + (c.p7 * t2) + (c.p8 * t3);
    const double nonlin = (c.p9 + (c.p10 * t_lin)) * p2 + (c.p11 * p3);

    return {
        .pressure_pa = offset + (sens * p_raw) + nonlin,
        .temperature_c = t_lin
    };
}

} // namespace drivers
