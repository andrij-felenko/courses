#include <stdint.h>

class LM35Driver {
public:
    struct Config {
        float vref_mv;          // Опорна напруга АЦП у мілівольтах
        uint8_t adc_bits;       // Розрядність АЦП (біти)
        float scale_factor;     // Коефіцієнт калібрування масштабу
        float offset_celsius;   // Коефіцієнт зміщення нуля (°C)
    };

    LM35Driver() : lsb_mv_(0.0f), max_adc_raw_(0) {}

    bool begin(const Config& config) {
        if (config.adc_bits == 0 || config.adc_bits > 16 || config.vref_mv <= 0.0f) {
            return false;
        }
        config_ = config;
        max_adc_raw_ = (1U << config_.adc_bits) - 1U;
        lsb_mv_ = config_.vref_mv / static_cast<float>(max_adc_raw_);
        return true;
    }

    float getLSB() const { return lsb_mv_; }

private:
    Config config_;
    float lsb_mv_;
    uint32_t max_adc_raw_;
};
