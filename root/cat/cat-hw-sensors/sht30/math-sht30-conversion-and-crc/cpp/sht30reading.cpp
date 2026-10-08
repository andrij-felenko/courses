#include <cstdint>
#include <algorithm>

struct SHT30Reading {
    int32_t temp_celsius_x100;    // Температура в 0.01 °C
    int32_t temp_fahrenheit_x100; // Температура в 0.01 °F
    uint16_t humidity_x100;       // Вологість в 0.01 % RH
};

class SHT30Converter {
public:
    static SHT30Reading process(uint16_t raw_temp, uint16_t raw_humidity) noexcept {
        SHT30Reading result{};

        // Обчислення Цельсія
        int64_t temp_c_num = static_cast<int64_t>(17500) * raw_temp + 32767;
        result.temp_celsius_x100 = static_cast<int32_t>(-4500 + (temp_c_num / 65535));

        // Обчислення Фаренгейта
        int64_t temp_f_num = static_cast<int64_t>(31500) * raw_temp + 32767;
        result.temp_fahrenheit_x100 = static_cast<int32_t>(-4900 + (temp_f_num / 65535));

        // Обчислення вологості
        uint64_t rh_num = static_cast<uint64_t>(10000) * raw_humidity + 32767;
        uint32_t rh_scaled = static_cast<uint32_t>(rh_num / 65535);
        result.humidity_x100 = static_cast<uint16_t>(std::min(rh_scaled, uint32_t{10000}));

        return result;
    }
};
