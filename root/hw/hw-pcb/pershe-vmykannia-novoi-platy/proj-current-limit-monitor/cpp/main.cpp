#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <chrono>
#include <concepts>
#include <algorithm>

namespace hw::protection {

using namespace std::chrono_literals;

struct Milliamperes {
    int32_t value{0};
    constexpr auto operator<=>(const Milliamperes&) const = default;
};

struct Millivolts {
    uint32_t value{0};
    constexpr auto operator<=>(const Millivolts&) const = default;
};

struct Milliwatts {
    uint32_t value{0};
    constexpr auto operator<=>(const Milliwatts&) const = default;
};

constexpr Milliamperes operator""_mA(unsigned long long v) {
    return Milliamperes{static_cast<int32_t>(v)};
}

constexpr Millivolts operator""_mV(unsigned long long v) {
    return Millivolts{static_cast<uint32_t>(v)};
}

constexpr Milliwatts operator""_mW(unsigned long long v) {
    return Milliwatts{static_cast<uint32_t>(v)};
}

enum class ErrorCode : uint8_t {
    I2cCommunicationFailure,
    DeviceNotResponding,
    ConfigurationMismatch,
    CalibrationError,
    OverCurrentTrip,
    OverVoltageTrip,
    BrownoutTrip,
    HardwareLatchTriggered
};

struct TelemetrySample {
    std::chrono::milliseconds timestamp{0};
    Milliamperes current{0_mA};
    Millivolts voltage{0_mV};
    Milliwatts power{0_mW};
};

template <size_t Capacity>
class RingBufferTrace {
public:
    constexpr RingBufferTrace() = default;

    void push(const TelemetrySample& sample) noexcept {
        if (m_locked) return;
        m_data[m_head] = sample;
        m_head = (m_head + 1) % Capacity;
        if (m_size < Capacity) {
            ++m_size;
        }
    }

    void lock() noexcept {
        m_locked = true;
    }

    [[nodiscard]] bool is_locked() const noexcept {
        return m_locked;
    }

    [[nodiscard]] size_t size() const noexcept {
        return m_size;
    }

    [[nodiscard]] std::array<TelemetrySample, Capacity> snapshot_ordered() const noexcept {
        std::array<TelemetrySample, Capacity> result{};
        if (m_size == 0) return result;

        size_t start_idx = (m_size == Capacity) ? m_head : 0;
        for (size_t i = 0; i < m_size; ++i) {
            result[i] = m_data[(start_idx + i) % Capacity];
        }
        return result;
    }

private:
    std::array<TelemetrySample, Capacity> m_data{};
    size_t m_head{0};
    size_t m_size{0};
    bool m_locked{false};
};

template <typename I2cBus, typename GpioSwitch, typename ClockSource>
class CurrentLimitMonitor {
public:
    struct Config {
        uint8_t i2c_address{0x40};
        uint16_t calibration_reg{2560};
        Milliamperes current_limit{500_mA};
        Millivolts min_voltage{4500_mV};
        Millivolts max_voltage{5500_mV};
        std::chrono::milliseconds inrush_grace{30ms};
    };

    enum class State : uint8_t {
        Disarmed,
        SoftStart,
        Armed,
        TrippedOverCurrent,
        TrippedOverVoltage,
        TrippedBrownout,
        TrippedHardwareLatch
    };

    explicit CurrentLimitMonitor(I2cBus& i2c, GpioSwitch& sw, ClockSource& clock, Config cfg) noexcept
        : m_i2c{i2c}, m_switch{sw}, m_clock{clock}, m_config{cfg} {}

    ~CurrentLimitMonitor() noexcept {
        // RAII: Гарантоване знеструмлення при знищенні об'єкта
        m_switch.disable();
    }

    CurrentLimitMonitor(const CurrentLimitMonitor&) = delete;
    CurrentLimitMonitor& operator=(const CurrentLimitMonitor&) = delete;
    CurrentLimitMonitor(CurrentLimitMonitor&&) noexcept = default;
    CurrentLimitMonitor& operator=(CurrentLimitMonitor&&) noexcept = default;

    [[nodiscard]] std::expected<void, ErrorCode> init() noexcept {
        m_switch.disable();
        m_state = State::Disarmed;

        // Скидання конфігурації INA226
        if (!write_register(0x00, 0x8000)) {
            return std::unexpected(ErrorCode::I2cCommunicationFailure);
        }

        // Конфігурація: 16x усереднення, 1.1 мс час конверсії, безперервний режим
        uint16_t cfg_word = (0x02 << 9) | (0x04 << 6) | (0x04 << 3) | 0x07;
        if (!write_register(0x00, cfg_word)) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        // Запис регістра калібрування
        if (!write_register(0x05, m_config.calibration_reg)) {
            return std::unexpected(ErrorCode::CalibrationError);
        }

        // Налаштування аварійного порогу ALERT
        int16_t alert_raw = static_cast<int16_t>((m_config.current_limit.value * 1000) / 200);
        if (!write_register(0x07, static_cast<uint16_t>(alert_raw))) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        // Увімкнення переривання за перевищенням струму шунта (SOL + APOL + LEN)
        uint16_t mask = (1 << 15) | (1 << 1) | (1 << 0);
        if (!write_register(0x06, mask)) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, ErrorCode> arm() noexcept {
        if (m_state != State::Disarmed) {
            return std::unexpected(ErrorCode::ConfigurationMismatch);
        }
        m_arm_start_time = m_clock.now();
        m_state = State::SoftStart;
        m_switch.enable();
        return {};
    }

    void handle_hardware_trip_isr() noexcept {
        m_switch.disable();
        m_state = State::TrippedHardwareLatch;
        m_trace.lock();
    }

    [[nodiscard]] std::expected<TelemetrySample, ErrorCode> poll() noexcept {
        if (m_state == State::Disarmed || is_tripped()) {
            return std::unexpected(ErrorCode::HardwareLatchTriggered);
        }

        auto now = m_clock.now();
        auto raw_vbus = read_register(0x02);
        auto raw_curr = read_register(0x04);
        auto raw_pwr  = read_register(0x03);
        auto raw_mask = read_register(0x06);

        if (!raw_vbus || !raw_curr || !raw_pwr || !raw_mask) {
            trip(State::TrippedHardwareLatch);
            return std::unexpected(ErrorCode::I2cCommunicationFailure);
        }

        auto signed_curr = static_cast<int16_t>(*raw_curr);
        Milliamperes current{static_cast<int32_t>(signed_curr * 200 / 1000)};
        Millivolts voltage{static_cast<uint32_t>(*raw_vbus * 1250 / 1000)};
        Milliwatts power{static_cast<uint32_t>(*raw_pwr * 5000 / 1000)};

        TelemetrySample sample{now, current, voltage, power};
        m_trace.push(sample);

        // Перевірка часу завершення м'якого старту
        if (m_state == State::SoftStart) {
            if (now - m_arm_start_time >= m_config.inrush_grace) {
                m_state = State::Armed;
            }
        }

        // Апаратний прапорець виходу за межі
        if (*raw_mask & (1 << 4)) {
            trip(State::TrippedOverCurrent);
            return std::unexpected(ErrorCode::OverCurrentTrip);
        }

        // Валідація напруги
        if (voltage > m_config.max_voltage) {
            trip(State::TrippedOverVoltage);
            return std::unexpected(ErrorCode::OverVoltageTrip);
        }

        if (m_state == State::Armed && voltage < m_config.min_voltage) {
            trip(State::TrippedBrownout);
            return std::unexpected(ErrorCode::BrownoutTrip);
        }

        // Програмна перевірка струму
        if (m_state == State::Armed && current > m_config.current_limit) {
            trip(State::TrippedOverCurrent);
            return std::unexpected(ErrorCode::OverCurrentTrip);
        }

        return sample;
    }

    [[nodiscard]] State state() const noexcept { return m_state; }
    [[nodiscard]] bool is_tripped() const noexcept {
        return m_state == State::TrippedOverCurrent ||
               m_state == State::TrippedOverVoltage ||
               m_state == State::TrippedBrownout ||
               m_state == State::TrippedHardwareLatch;
    }

    [[nodiscard]] const RingBufferTrace<256>& trace() const noexcept { return m_trace; }

private:
    void trip(State reason) noexcept {
        m_switch.disable();
        m_state = reason;
        m_trace.lock();
    }

    [[nodiscard]] bool write_register(uint8_t reg, uint16_t val) noexcept {
        uint16_t swapped = static_cast<uint16_t>((val << 8) | (val >> 8));
        return m_i2c.write(m_config.i2c_address, reg, swapped);
    }

    [[nodiscard]] std::optional<uint16_t> read_register(uint8_t reg) noexcept {
        auto val = m_i2c.read(m_config.i2c_address, reg);
        if (!val) return std::nullopt;
        return static_cast<uint16_t>((*val << 8) | (*val >> 8));
    }

    I2cBus& m_i2c;
    GpioSwitch& m_switch;
    ClockSource& m_clock;
    Config m_config;
    State m_state{State::Disarmed};
    std::chrono::milliseconds m_arm_start_time{0ms};
    RingBufferTrace<256> m_trace{};
};

} // namespace hw::protection
