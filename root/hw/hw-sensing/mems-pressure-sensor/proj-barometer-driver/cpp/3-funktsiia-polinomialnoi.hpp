namespace drivers {

class BaroCompensator {
public:
    [[nodiscard]] static constexpr double compensate_temperature(const BaroCalibCoeffs& c, uint32_t raw_temp) noexcept {
        const double dt = static_cast<double>(raw_temp) - c.t1;
        return (dt * c.t2) + (dt * dt * c.t3);
    }

    [[nodiscard]] static constexpr double compensate_pressure(const BaroCalibCoeffs& c, uint32_t raw_press, double t_lin) noexcept {
        const double t2 = t_lin * t_lin;
        const double t3 = t2 * t_lin;
        const double p_raw = static_cast<double>(raw_press);
        const double p2 = p_raw * p_raw;
        const double p3 = p2 * p_raw;

        const double offset = c.p1 + (c.p2 * t_lin) + (c.p3 * t2) + (c.p4 * t3);
        const double sens   = c.p5 + (c.p6 * t_lin) + (c.p7 * t2) + (c.p8 * t3);
        const double nonlin = (c.p9 + (c.p10 * t_lin)) * p2 + (c.p11 * p3);

        return offset + (sens * p_raw) + nonlin;
    }
};

} // namespace drivers
