#include <cstdint>
#include <cstddef>

class LvdtDriver {
public:
    struct Config {
        uint32_t carrier_freq_hz;        // Частота сигналу збудження (Гц)
        uint16_t adc_samples_per_period; // Кількість відліків АЦП на період
        float    min_sum_threshold;      // Поріг суми напруг для виявлення обриву
        float    max_ratio_limit;        // Граничне допустиме ратіометричне значення
    };

    struct Calibration {
        float zero_offset_ratio;         // Зсув електричного нуля (V_zero)
        float scale_factor_mm;           // Масштабний коефіцієнт (K_scale, мм)
        float poly_c0;                   // Поліноміальний коефіцієнт c0
        float poly_c1;                   // Поліноміальний коефіцієнт c1
        float poly_c2;                   // Поліноміальний коефіцієнт c2
        float poly_c3;                   // Поліноміальний коефіцієнт c3
    };

    enum class Status : uint32_t {
        Ok             = 0x00,
        InvalidParam   = 0x01,
        ExcitationLost = 0x02,
        WindingFault   = 0x04,
        OutOfRange     = 0x08
    };

    LvdtDriver() = default;

    Status init(const Config& config, const Calibration& calib) {
        config_ = config;
        calib_ = calib;
        status_ = Status::Ok;
        last_raw_ratio_ = 0.0f;
        last_position_mm_ = 0.0f;
        return Status::Ok;
    }

    Status getStatus() const { return status_; }
    float getPositionMm() const { return last_position_mm_; }

private:
    Config      config_{};
    Calibration calib_{};
    Status      status_{Status::Ok};
    float       last_raw_ratio_{0.0f};
    float       last_position_mm_{0.0f};
};
