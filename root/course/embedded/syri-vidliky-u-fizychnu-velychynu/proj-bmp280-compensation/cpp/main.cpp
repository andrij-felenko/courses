#include <cstdint>
#include <array>
#include <span>
#include <optional>

namespace sensor {

struct CalibrationData {
    uint16_t dig_T1{0};
    int16_t  dig_T2{0};
    int16_t  dig_T3{0};
    uint16_t dig_P1{0};
    int16_t  dig_P2{0};
    int16_t  dig_P3{0};
    int16_t  dig_P4{0};
    int16_t  dig_P5{0};
    int16_t  dig_P6{0};
    int16_t  dig_P7{0};
    int16_t  dig_P8{0};
    int16_t  dig_P9{0};
};

struct MeasurementResult {
    int32_t  temperature_centi_deg; // 0.01 °C
    uint32_t pressure_pa;           // Цілі Паскалі
};

class Bmp280Engine {
public:
    constexpr Bmp280Engine() = default;

    // Безпечний розбір сирого масиву калібрування через std::span
    bool load_calibration(std::span<const uint8_t, 24> buf) noexcept {
        auto read_u16 = [](const uint8_t* p) constexpr -> uint16_t {
            return static_cast<uint16_t>(p[0] | (static_cast<uint16_t>(p[1]) << 8));
        };
        auto read_s16 = [](const uint8_t* p) constexpr -> int16_t {
            return static_cast<int16_t>(p[0] | (static_cast<uint16_t>(p[1]) << 8));
        };

        calib_.dig_T1 = read_u16(&buf[0]);
        calib_.dig_T2 = read_s16(&buf[2]);
        calib_.dig_T3 = read_s16(&buf[4]);
        calib_.dig_P1 = read_u16(&buf[6]);
        calib_.dig_P2 = read_s16(&buf[8]);
        calib_.dig_P3 = read_s16(&buf[10]);
        calib_.dig_P4 = read_s16(&buf[12]);
        calib_.dig_P5 = read_s16(&buf[14]);
        calib_.dig_P6 = read_s16(&buf[16]);
        calib_.dig_P7 = read_s16(&buf[18]);
        calib_.dig_P8 = read_s16(&buf[20]);
        calib_.dig_P9 = read_s16(&buf[22]);

        return calib_.dig_T1 != 0 && calib_.dig_P1 != 0;
    }

    // Компенсація температури
    [[nodiscard]] int32_t compensate_temperature(int32_t adc_T) noexcept {
        const int32_t var1 = ((((adc_T >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) * 
                               static_cast<int32_t>(calib_.dig_T2)) >> 11;

        const int32_t diff = (adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1);
        const int32_t var2 = (((diff * diff) >> 12) * static_cast<int32_t>(calib_.dig_T3)) >> 14;

        t_fine_ = var1 + var2;
        return (t_fine_ * 5 + 128) >> 8;
    }

    // Компенсація тиску в цілих Паскалях
    [[nodiscard]] std::optional<uint32_t> compensate_pressure(int32_t adc_P) const noexcept {
        int64_t var1 = static_cast<int64_t>(t_fine_) - 128000;
        int64_t var2 = var1 * var1 * static_cast<int64_t>(calib_.dig_P6);
        var2 += (var1 * static_cast<int64_t>(calib_.dig_P5)) << 17;
        var2 += static_cast<int64_t>(calib_.dig_P4) << 35;
        
        var1 = ((var1 * var1 * static_cast<int64_t>(calib_.dig_P3)) >> 8) + 
               ((var1 * static_cast<int64_t>(calib_.dig_P2)) << 12);
        var1 = ((static_cast<int64_t>(1) << 47) + var1) * static_cast<int64_t>(calib_.dig_P1) >> 33;

        if (var1 == 0) {
            return std::nullopt; // Помилка: ділення на нуль
        }

        int64_t p = 1048576 - adc_P;
        p = (((p << 31) - var2) * 3125) / var1;
        
        const int64_t p_shift = p >> 13;
        var1 = (static_cast<int64_t>(calib_.dig_P9) * p_shift * p_shift) >> 25;
        var2 = (static_cast<int64_t>(calib_.dig_P8) * p) >> 19;

        p = ((p + var1 + var2) >> 8) + (static_cast<int64_t>(calib_.dig_P7) << 4);
        
        // Переведення з формату Q24.8 у цілі Паскалі
        return static_cast<uint32_t>(p >> 8);
    }

    // Комплексна обробка 6-байтного кадру вимірювання
    [[nodiscard]] std::optional<MeasurementResult> process_raw_frame(std::span<const uint8_t, 6> frame) noexcept {
        const int32_t raw_p = (static_cast<int32_t>(frame[0]) << 12) |
                              (static_cast<int32_t>(frame[1]) << 4)  |
                              (static_cast<int32_t>(frame[2]) >> 4);

        const int32_t raw_t = (static_cast<int32_t>(frame[3]) << 12) |
                              (static_cast<int32_t>(frame[4]) << 4)  |
                              (static_cast<int32_t>(frame[5]) >> 4);

        const int32_t temp = compensate_temperature(raw_t);
        const auto press = compensate_pressure(raw_p);
        
        if (!press) {
            return std::nullopt;
        }

        return MeasurementResult{
            .temperature_centi_deg = temp,
            .pressure_pa = *press
        };
    }

private:
    CalibrationData calib_{};
    int32_t t_fine_{0};
};

} // namespace sensor
