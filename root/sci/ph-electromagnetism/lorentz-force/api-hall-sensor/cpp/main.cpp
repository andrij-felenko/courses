#include <cstdint>
#include <cmath>
#include <algorithm>
#include <array>

class HallSensorSS49E {
public:
    struct Config {
        float vcc{5.0f};           // Напруга живлення (В)
        float sensitivity{0.014f};  // Чутливість: 14.0 мВ/мТл = 0.014 В/мТл
        uint16_t adc_max{4095};    // 12-бітний АЦП (2^12 - 1)
        size_t filter_samples{16}; // Кількість усереднень
    };

    explicit HallSensorSS49E(Config config)
        : cfg_(config), v_quiescent_(config.vcc * 0.5f) {}

    // Калібрування нуля при відсутності магнітного поля
    void calibrate_zero(const float* raw_adc_samples, size_t count) {
        if (count == 0 || raw_adc_samples == nullptr) return;

        float sum_v = 0.0f;
        for (size_t i = 0; i < count; ++i) {
            sum_v += (raw_adc_samples[i] / static_cast<float>(cfg_.adc_max)) * cfg_.vcc;
        }
        v_quiescent_ = sum_v / static_cast<float>(count);
    }

    // Перетворення виміряного коду АЦП у магнітну індукцію (в мТл)
    [[nodiscard]] float convert_adc_to_mT(uint16_t adc_raw) const {
        float v_out = (static_cast<float>(adc_raw) / static_cast<float>(cfg_.adc_max)) * cfg_.vcc;
        return (v_out - v_quiescent_) / cfg_.sensitivity;
    }

    [[nodiscard]] float quiescent_voltage() const { return v_quiescent_; }

private:
    Config cfg_;
    float v_quiescent_;
};
