#include <cstdint>
#include <cmath>
#include <expected>
#include <optional>
#include <span>

namespace embedded {

enum class AdcError {
    HardwareTimeout,
    SpiCommunicationFailure,
    CalculationOutOfRange
};

class Ads1220Rtd {
public:
    struct SpiInterface {
        void (*cs_assert)();
        void (*cs_deassert)();
        void (*transfer)(std::span<const uint8_t> tx, std::span<uint8_t> rx);
        bool (*wait_drdy_low)(uint32_t timeout_ms);
    };

    static constexpr float Pt100R0 = 100.0f;
    static constexpr float Pt100A  = 3.9083e-3f;
    static constexpr float Pt100B  = -5.7750e-7f;
    static constexpr float Pt100C  = -4.1830e-12f;

    explicit Ads1220Rtd(SpiInterface bus, float r_ref = 3300.0f, float gain = 16.0f)
        : bus_(bus), r_ref_(r_ref), gain_(gain), offset_code_(0) {}

    bool init() {
        // Скидання мікросхеми
        const uint8_t cmd_reset = 0x06;
        execute_transaction(std::span(&cmd_reset, 1), {});

        // Конфігурація регістрів 0..3
        const uint8_t config[5] = {
            0x43, // WREG starting from register 0, length = 4
            0x38, // AIN1-AIN2 diff, Gain=16, PGA on
            0x00, // 20 SPS, Single-shot, Normal mode
            0x76, // External Vref REFP0/REFN0, FIR 50/60Hz, IDAC=500 uA
            0x60  // IDAC1 -> AIN0, IDAC2 -> AIN1
        };

        execute_transaction(std::span(config, 5), {});
        return true;
    }

    bool calibrate_offset() {
        const uint8_t cal_cfg[2] = { 0x40, 0xE8 }; // MUX = (AVDD-AVSS)/2, Gain=16
        execute_transaction(std::span(cal_cfg, 2), {});

        const uint8_t cmd_start = 0x08;
        execute_transaction(std::span(&cmd_start, 1), {});

        if (!bus_.wait_drdy_low(60)) return false;

        const uint8_t tx[4] = { 0x10, 0x00, 0x00, 0x00 };
        uint8_t rx[4] = { 0 };
        execute_transaction(std::span(tx, 4), std::span(rx, 4));

        int32_t offset = (static_cast<int32_t>(rx[1]) << 16) |
                         (static_cast<int32_t>(rx[2]) << 8)  |
                         (static_cast<int32_t>(rx[3]));
        if (offset & 0x00800000) offset |= 0xFF000000;
        offset_code_ = offset;

        // Повернення в робочий режим
        const uint8_t restore_cfg[2] = { 0x40, 0x38 };
        execute_transaction(std::span(restore_cfg, 2), {});
        return true;
    }

    std::expected<int32_t, AdcError> read_raw() const {
        const uint8_t cmd_start = 0x08;
        execute_transaction(std::span(&cmd_start, 1), {});

        if (!bus_.wait_drdy_low(60)) {
            return std::unexpected(AdcError::HardwareTimeout);
        }

        const uint8_t tx[4] = { 0x10, 0x00, 0x00, 0x00 };
        uint8_t rx[4] = { 0 };
        execute_transaction(std::span(tx, 4), std::span(rx, 4));

        int32_t code = (static_cast<int32_t>(rx[1]) << 16) |
                       (static_cast<int32_t>(rx[2]) << 8)  |
                       (static_cast<int32_t>(rx[3]));

        if (code & 0x00800000) {
            code |= 0xFF000000;
        }

        return code - offset_code_;
    }

    std::expected<float, AdcError> read_temperature() const {
        auto raw = read_raw();
        if (!raw) return std::unexpected(raw.error());

        // Логометричний перерахунок опору
        const float r_pt100 = (static_cast<float>(*raw) * 2.0f * r_ref_) / (8388608.0f * gain_);

        // Розв'язання рівняння Каллендара-Ван Дюзена для T >= 0 °C
        const float z = 1.0f - (r_pt100 / Pt100R0);
        const float discriminant = (Pt100A * Pt100A) - (4.0f * Pt100B * z);

        if (discriminant < 0.0f) {
            return std::unexpected(AdcError::CalculationOutOfRange);
        }

        float temp = (-Pt100A + std::sqrt(discriminant)) / (2.0f * Pt100B);

        // Уточнення за методом Ньютона для від'ємного діапазону
        if (temp < 0.0f) {
            for (int i = 0; i < 3; ++i) {
                const float t2 = temp * temp;
                const float t3 = t2 * temp;
                const float r_calc = Pt100R0 * (1.0f + Pt100A * temp + Pt100B * t2 + Pt100C * (temp - 100.0f) * t3);
                const float r_diff = Pt100R0 * (Pt100A + 2.0f * Pt100B * temp - 300.0f * Pt100C * t2 + 4.0f * Pt100C * t3);
                temp = temp - (r_calc - r_pt100) / r_diff;
            }
        }

        return temp;
    }

private:
    void execute_transaction(std::span<const uint8_t> tx, std::span<uint8_t> rx) const {
        bus_.cs_assert();
        bus_.transfer(tx, rx);
        bus_.cs_deassert();
    }

    SpiInterface bus_;
    float r_ref_;
    float gain_;
    int32_t offset_code_;
};

} // namespace embedded
