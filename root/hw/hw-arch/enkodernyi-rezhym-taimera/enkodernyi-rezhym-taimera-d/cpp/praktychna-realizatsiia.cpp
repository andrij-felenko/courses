#include <cstdint>
#include <concepts>
#include <numbers>
#include <atomic>

/* Апаратне відображення регістрів таймера */
struct TimerHardware {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
};

/* Режими множення квадратурного декодера */
enum class EncoderMode : uint32_t {
    X1_TI1 = 0x1, /* Рахунок лише на каналі TI1 */
    X2_TI2 = 0x2, /* Рахунок лише на каналі TI2 */
    X4_TI12 = 0x3 /* Повний квадратурний рахунок на обох каналах */
};

/* Рівень цифрової фільтрації вхідних каналів ICxF */
enum class FilterLevel : uint32_t {
    None = 0x0,
    Samples2_CK_INT = 0x1,
    Samples4_CK_INT = 0x2,
    Samples8_CK_INT = 0x3,
    Samples6_DTS_Div4 = 0x6,
    Samples8_DTS_Div32 = 0xF /* Максимальне придушення брязкоту контактів */
};

/* Знімок стану енкодера для атомарного передавання в контури керування */
struct EncoderSnapshot {
    int64_t total_ticks{0};
    double angle_rad{0.0};
    float velocity_rad_s{0.0f};
    bool is_reverse{false};
};

/* RAII-драйвер енкодерного інтерфейсу таймера */
template <uintptr_t TimerBaseAddress>
class QuadratureEncoder {
public:
    static TimerHardware& hardware() noexcept {
        return *reinterpret_cast<TimerHardware*>(TimerBaseAddress);
    }

    struct Config {
        uint32_t pulses_per_revolution{1024};
        EncoderMode mode{EncoderMode::X4_TI12};
        FilterLevel filter{FilterLevel::Samples8_CK_INT};
        bool invert_direction{false};
        float velocity_filter_cutoff_hz{50.0f};
        float update_period_s{0.001f};
    };

    explicit QuadratureEncoder(const Config& cfg) noexcept
        : counts_per_rev_(cfg.pulses_per_revolution * (cfg.mode == EncoderMode::X4_TI12 ? 4 : 2)),
          dt_(cfg.update_period_s) {
        init_hardware(cfg);
        init_filter(cfg.velocity_filter_cutoff_hz);
    }

    ~QuadratureEncoder() noexcept {
        hardware().CR1 &= ~1U; // Зупинка таймера
    }

    /* Заборона копіювання (апаратний ресурс унікальний) */
    QuadratureEncoder(const QuadratureEncoder&) = delete;
    QuadratureEncoder& operator=(const QuadratureEncoder&) = delete;
    QuadratureEncoder(QuadratureEncoder&&) noexcept = default;
    QuadratureEncoder& operator=(QuadratureEncoder&&) noexcept = default;

    /* Періодичне оновлення стану (виклик з ISR періоду керування або RTOS потоку) */
    void update() noexcept {
        const auto current_cnt = static_cast<uint16_t>(hardware().CNT);
        const auto delta = static_cast<int16_t>(current_cnt - last_cnt_);
        last_cnt_ = current_cnt;

        total_position_ += delta;

        // Миттєва швидкість
        const float instant_velocity = (static_cast<float>(delta) / static_cast<float>(counts_per_rev_)) *
                                       (2.0f * std::numbers::pi_v<float>) / dt_;

        // Фільтрація першого порядку
        velocity_rad_s_ += lpf_alpha_ * (instant_velocity - velocity_rad_s_);

        // Оновлення кешованого знімка
        const bool reverse = (hardware().CR1 & (1U << 4)) != 0;
        snapshot_.store({
            .total_ticks = total_position_,
            .angle_rad = (static_cast<double>(total_position_) / counts_per_rev_) * (2.0 * std::numbers::pi_v<double>),
            .velocity_rad_s = velocity_rad_s_,
            .is_reverse = reverse
        }, std::memory_order_relaxed);
    }

    [[nodiscard]] EncoderSnapshot get_snapshot() const noexcept {
        return snapshot_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] int64_t get_ticks() const noexcept {
        return total_position_;
    }

    [[nodiscard]] float get_velocity() const noexcept {
        return velocity_rad_s_;
    }

    void reset_position() noexcept {
        hardware().CNT = 0;
        last_cnt_ = 0;
        total_position_ = 0;
        velocity_rad_s_ = 0.0f;
    }

private:
    void init_hardware(const Config& cfg) noexcept {
        auto& tim = hardware();

        tim.CR1 = 0; // Вимкнення лічильника

        const auto filter_val = static_cast<uint32_t>(cfg.filter);
        // Канал 1: CC1S = 01, IC1F = filter; Канал 2: CC2S = 01, IC2F = filter
        tim.CCMR1 = (0x1U << 0) | (filter_val << 4) | (0x1U << 8) | (filter_val << 12);

        // Полярність входів (інверсія за потреби)
        tim.CCER = cfg.invert_direction ? (1U << 1) : 0U; // CC1P інвертує канал A

        // Встановлення режиму декодера в SMCR
        tim.SMCR = static_cast<uint32_t>(cfg.mode);

        tim.ARR = 0xFFFFU; // 16-бітний максимальний період
        tim.PSC = 0;
        tim.CNT = 0;

        tim.CR1 |= (1U << 0); // Старт таймера (CEN = 1)
        last_cnt_ = static_cast<uint16_t>(tim.CNT);
    }

    void init_filter(float cutoff_hz) noexcept {
        if (cutoff_hz > 0.0f) {
            const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
            lpf_alpha_ = dt_ / (dt_ + rc);
        } else {
            lpf_alpha_ = 1.0f;
        }
    }

    uint32_t counts_per_rev_{4096};
    float dt_{0.001f};
    float lpf_alpha_{1.0f};
    uint16_t last_cnt_{0};
    int64_t total_position_{0};
    float velocity_rad_s_{0.0f};
    std::atomic<EncoderSnapshot> snapshot_{};
};
