// rf_frontend.hpp — Драйвер ВЧ-переднього кінця мовою C++20
#pragma once

#include <cstdint>
#include <expected>
#include <optional>

namespace rf {

enum class Mode : uint8_t {
    Shutdown,
    RxHighGain,
    RxBypass,
    Tx
};

enum class Error : uint8_t {
    InvalidMode,
    Overtemperature,
    HighVswr,
    HardwareFault
};

struct Telemetry {
    float temp_celsius{0.0f};
    float forward_power_dbm{0.0f};
    float reverse_power_dbm{0.0f};
    float vswr{1.0f};
};

class FrontEndModule {
public:
    static constexpr float MaxTempCelsius = 85.0f;
    static constexpr float MaxVswr = 3.0f;

    FrontEndModule() noexcept = default;
    ~FrontEndModule() { (void)shutdown(); }

    // Заборона копіювання (RAII керування апаратним ресурсом)
    FrontEndModule(const FrontEndModule&) = delete;
    FrontEndModule& operator=(const FrontEndModule&) = delete;
    FrontEndModule(FrontEndModule&&) noexcept = default;
    FrontEndModule& operator=(FrontEndModule&&) noexcept = default;

    [[nodiscard]] std::expected<void, Error> set_mode(Mode new_mode) noexcept;
    [[nodiscard]] Mode current_mode() const noexcept { return mode_; }
    [[nodiscard]] std::expected<Telemetry, Error> update_telemetry() noexcept;
    [[nodiscard]] std::expected<void, Error> shutdown() noexcept;

private:
    Mode mode_{Mode::Shutdown};

    void apply_gpio_pins(bool tx_en, bool rx_en, bool bypass, bool pa_bias) noexcept;
    float read_adc_pa_temp() const noexcept;
    float read_adc_fwd_pwr() const noexcept;
    float read_adc_rev_pwr() const noexcept;
    void delay_us(uint32_t us) const noexcept;
};

inline std::expected<void, Error> FrontEndModule::shutdown() noexcept {
    apply_gpio_pins(false, false, true, false);
    mode_ = Mode::Shutdown;
    return {};
}

inline std::expected<void, Error> FrontEndModule::set_mode(Mode new_mode) noexcept {
    if (new_mode == mode_) {
        return {};
    }

    if (new_mode == Mode::Tx) {
        if (read_adc_pa_temp() > MaxTempCelsius) {
            (void)shutdown();
            return std::unexpected(Error::Overtemperature);
        }
    }

    // Безпечна деактивація попереднього режиму
    if (mode_ == Mode::Tx) {
        apply_gpio_pins(true, false, true, false); // Знімаємо bias
        delay_us(5);
        apply_gpio_pins(false, false, true, false); // Вимикаємо TX ключ
        delay_us(2);
    } else if (mode_ == Mode::RxHighGain || mode_ == Mode::RxBypass) {
        apply_gpio_pins(false, false, true, false); // Вимикаємо RX
        delay_us(2);
    }

    // Активація нового режиму
    switch (new_mode) {
        case Mode::Shutdown:
            return shutdown();

        case Mode::RxHighGain:
            apply_gpio_pins(false, true, false, false);
            break;

        case Mode::RxBypass:
            apply_gpio_pins(false, true, true, false);
            break;

        case Mode::Tx:
            apply_gpio_pins(true, false, true, false);
            delay_us(5);
            apply_gpio_pins(true, false, true, true); // Подаємо bias на PA
            break;
    }

    mode_ = new_mode;
    return {};
}

inline std::expected<Telemetry, Error> FrontEndModule::update_telemetry() noexcept {
    Telemetry t{};
    t.temp_celsius = read_adc_pa_temp();
    t.forward_power_dbm = read_adc_fwd_pwr();
    t.reverse_power_dbm = read_adc_rev_pwr();

    float p_fwd_mw = 0.001f * t.forward_power_dbm;
    float p_rev_mw = 0.001f * t.reverse_power_dbm;

    if (p_fwd_mw > 0.001f) {
        float gamma = (p_rev_mw < p_fwd_mw) ? (p_rev_mw / p_fwd_mw) : 0.99f;
        t.vswr = (1.0f + gamma) / (1.0f - gamma + 0.0001f);
    }

    if (mode_ == Mode::Tx && t.vswr > MaxVswr) {
        (void)shutdown();
        return std::unexpected(Error::HighVswr);
    }

    return t;
}

inline void FrontEndModule::apply_gpio_pins(bool tx_en, bool rx_en, bool bypass, bool pa_bias) noexcept {
    // Взаємодія з HAL МК
    (void)tx_en; (void)rx_en; (void)bypass; (void)pa_bias;
}
inline float FrontEndModule::read_adc_pa_temp() const noexcept { return 45.0f; }
inline float FrontEndModule::read_adc_fwd_pwr() const noexcept { return 30.0f; }
inline float FrontEndModule::read_adc_rev_pwr() const noexcept { return 0.5f; }
inline void FrontEndModule::delay_us(uint32_t us) const noexcept { (void)us; }

} // namespace rf
