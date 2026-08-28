namespace drivers {

class MemsBarometerParser {
public:
    [[nodiscard]] static constexpr BaroCalibCoeffs parse_calibration(std::span<const uint8_t, 21> nvm) noexcept {
        BaroCalibCoeffs c{};

        const auto raw_t1 = static_cast<uint16_t>(nvm[0] | (nvm[1] << 8));
        const auto raw_t2 = static_cast<uint16_t>(nvm[2] | (nvm[3] << 8));
        const auto raw_t3 = static_cast<int8_t>(nvm[4]);

        const auto raw_p1 = static_cast<int16_t>(nvm[5] | (nvm[6] << 8));
        const auto raw_p2 = static_cast<int16_t>(nvm[7] | (nvm[8] << 8));
        const auto raw_p3 = static_cast<int8_t>(nvm[9]);
        const auto raw_p4 = static_cast<int8_t>(nvm[10]);
        const auto raw_p5 = static_cast<uint16_t>(nvm[11] | (nvm[12] << 8));
        const auto raw_p6 = static_cast<uint16_t>(nvm[13] | (nvm[14] << 8));
        const auto raw_p7 = static_cast<int8_t>(nvm[15]);
        const auto raw_p8 = static_cast<int8_t>(nvm[16]);
        const auto raw_p9 = static_cast<int16_t>(nvm[17] | (nvm[18] << 8));
        const auto raw_p10 = static_cast<int8_t>(nvm[19]);
        const auto raw_p11 = static_cast<int8_t>(nvm[20]);

        c.t1 = static_cast<double>(raw_t1) * 256.0;
        c.t2 = static_cast<double>(raw_t2) / 1073741824.0;
        c.t3 = static_cast<double>(raw_t3) / 281474976710656.0;

        c.p1 = (static_cast<double>(raw_p1) - 16384.0) / 1048576.0;
        c.p2 = (static_cast<double>(raw_p2) - 16384.0) / 536870912.0;
        c.p3 = static_cast<double>(raw_p3) / 4294967296.0;
        c.p4 = static_cast<double>(raw_p4) / 137438953472.0;
        c.p5 = static_cast<double>(raw_p5) * 8.0;
        c.p6 = static_cast<double>(raw_p6) / 64.0;
        c.p7 = static_cast<double>(raw_p7) / 256.0;
        c.p8 = static_cast<double>(raw_p8) / 32768.0;
        c.p9 = static_cast<double>(raw_p9) / 281474976710656.0;
        c.p10 = static_cast<double>(raw_p10) / 281474976710656.0;
        c.p11 = static_cast<double>(raw_p11) / 36893488147419103232.0;

        return c;
    }
};

} // namespace drivers
