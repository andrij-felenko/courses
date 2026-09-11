#include <cstdint>

struct MotorCurrentConfig {
    uint16_t shunt_mohm{100};               // Опір шунта (100 мОм)
    uint16_t amplifier_gain{20};            // Підсилення сигналу шунта (20x)
    uint16_t adc_vref_mv{3300};             // Опорна напруга АЦП (3.3 В)
    uint16_t adc_max_ticks{4095};           // 12-бітний АЦП
    uint16_t stall_current_ma{800};         // Поріг струму при 100% ШІМ (800 мА)
    uint16_t min_stall_current_ma{250};     // Мінімальний поріг заклинювання (250 мА)
    uint16_t min_detect_duty_permille{150}; // Поріг активації захисту (150 проміле = 15%)
    uint16_t blanking_time_ms{80};          // Вікно бланкування пуску (80 мс)
    uint16_t stall_timeout_ms{250};         // Час підтвердження заклинювання (250 мс)
};

class StallDetector {
public:
    explicit StallDetector(const MotorCurrentConfig& cfg)
        : config_(cfg), filtered_current_ma_(0), motion_start_ms_(0),
          overcurrent_start_ms_(0), is_stalled_(false) {}

    uint16_t readCurrentMa() {
        uint16_t adc_raw = hal_adc_read_raw();

        uint32_t v_adc_uv = (static_cast<uint32_t>(adc_raw) * config_.adc_vref_mv * 1000UL) /
                            config_.adc_max_ticks;

        uint32_t divisor = static_cast<uint32_t>(config_.amplifier_gain) * config_.shunt_mohm;
        uint32_t instant_ma = (divisor > 0) ? (v_adc_uv * 1000UL) / divisor : 0;

        filtered_current_ma_ = static_cast<uint16_t>(
            (static_cast<uint32_t>(filtered_current_ma_) * 3UL + instant_ma) / 4UL
        );

        return filtered_current_ma_;
    }

    uint16_t calculateThresholdMa(uint16_t duty_permille) const {
        if (duty_permille < config_.min_detect_duty_permille) {
            return 0; // Нижче мінімальної шпаруватості захист не активується
        }
        if (duty_permille >= 1000) {
            return config_.stall_current_ma;
        }

        uint32_t duty_span = 1000UL - config_.min_detect_duty_permille;
        uint32_t current_span = static_cast<uint32_t>(config_.stall_current_ma) - config_.min_stall_current_ma;
        uint32_t duty_rel = static_cast<uint32_t>(duty_permille) - config_.min_detect_duty_permille;

        return static_cast<uint16_t>(
            config_.min_stall_current_ma + (duty_rel * current_span) / duty_span
        );
    }

    bool checkStall(bool is_motor_active, uint16_t duty_permille, uint32_t now_ms) {
        if (is_stalled_) {
            return true;
        }

        if (!is_motor_active) {
            motion_start_ms_ = 0;
            overcurrent_start_ms_ = 0;
            return false;
        }

        if (motion_start_ms_ == 0) {
            motion_start_ms_ = now_ms;
            overcurrent_start_ms_ = 0;
            return false;
        }

        if ((now_ms - motion_start_ms_) < config_.blanking_time_ms) {
            overcurrent_start_ms_ = 0;
            return false;
        }

        uint16_t dynamic_threshold = calculateThresholdMa(duty_permille);
        if (dynamic_threshold == 0) {
            overcurrent_start_ms_ = 0;
            return false;
        }

        uint16_t current_ma = readCurrentMa();

        if (current_ma >= dynamic_threshold) {
            if (overcurrent_start_ms_ == 0) {
                overcurrent_start_ms_ = now_ms;
            } else if ((now_ms - overcurrent_start_ms_) >= config_.stall_timeout_ms) {
                is_stalled_ = true;
                hal_hbridge_emergency_shutdown();
                return true;
            }
        } else {
            overcurrent_start_ms_ = 0;
        }

        return false;
    }

    void clearFault() {
        is_stalled_ = false;
        motion_start_ms_ = 0;
        overcurrent_start_ms_ = 0;
        filtered_current_ma_ = 0;
    }

    bool isStalled() const { return is_stalled_; }
    uint16_t getFilteredCurrentMa() const { return filtered_current_ma_; }

private:
    MotorCurrentConfig config_;
    uint16_t           filtered_current_ma_;
    uint32_t           motion_start_ms_;
    uint32_t           overcurrent_start_ms_;
    bool               is_stalled_;
};
