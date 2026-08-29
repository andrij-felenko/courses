#include "bsp/board.hpp"
#include "bsp/platform.hpp"
#include "i2c_sensors.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <memory>
#include <utility>

namespace bsp {
namespace {

using namespace std::chrono_literals;

/* Топологія плати живе тут і більше ніде: застосунок не знає ані виводів,
   ані полярності, ані того, що ключ домену відкривається нулем на затворі. */

struct LedDesc {
    Pin  pin;
    bool active_high;
    bool open_drain;
};

struct DomainDesc {
    Pin                       gate;
    bool                      gate_active_high;
    std::chrono::milliseconds settle;
    bool                      owns_bus;
};

constexpr std::array<LedDesc, 3> kLeds{{
    {{GpioPort::A, 5}, true,  false}, // SystemStatus
    {{GpioPort::B, 0}, false, false}, // Warning, активний нуль
    {{GpioPort::B, 1}, false, true }, // Comms, спільний анод
}};

constexpr std::array<DomainDesc, 3> kDomains{{
    {{GpioPort::C, 13}, false, 15ms, true }, // Sensors
    {{GpioPort::C, 14}, false, 20ms, false}, // Radio
    {{GpioPort::C, 15}, false, 10ms, false}, // Display
}};

constexpr Pin kI2cScl{GpioPort::B, 6};
constexpr Pin kI2cSda{GpioPort::B, 7};
constexpr Pin kChargerStat{GpioPort::A, 1}; // STAT контролера заряду, активний нуль

constexpr std::uint8_t  kAdcChannelVbat    = 4;
constexpr std::uint8_t  kAdcChannelVrefint = 17;
constexpr std::uint32_t kVbatDivider       = 2;     // дільник 1:2
constexpr std::uint32_t kAdcFullScale      = 4095;
constexpr std::uint32_t kVrefintCalMv      = 3000;  // заводський код знято при 3.000 В
constexpr auto          kBusLockTimeout    = 20ms;
constexpr auto          kFlushTimeout      = 50ms;

template <typename Enum>
[[nodiscard]] constexpr std::size_t index_of(Enum value) noexcept {
    return static_cast<std::size_t>(std::to_underlying(value));
}

/** Розрядна крива Li-Ion: напруга спокою → залишковий заряд. */
[[nodiscard]] std::uint8_t charge_percent(std::uint32_t mv) noexcept {
    struct Point {
        std::uint16_t mv;
        std::uint8_t  percent;
    };
    constexpr std::array<Point, 8> kCurve{{
        {4200, 100}, {4000, 85}, {3850, 70}, {3700, 50},
        {3600, 30},  {3500, 15}, {3400, 7},  {3000, 0},
    }};

    if (mv >= kCurve.front().mv) {
        return 100;
    }
    for (std::size_t i = 1; i < kCurve.size(); ++i) {
        if (mv >= kCurve[i].mv) {
            const std::uint32_t span_mv = kCurve[i - 1].mv - kCurve[i].mv;
            const std::uint32_t span_pc = kCurve[i - 1].percent - kCurve[i].percent;
            return static_cast<std::uint8_t>(kCurve[i].percent +
                                             ((mv - kCurve[i].mv) * span_pc) / span_mv);
        }
    }
    return 0;
}

class BoardImpl final : public IBoardSupport {
public:
    explicit BoardImpl(IPlatform& platform) noexcept
        : platform_{platform}, sht_{platform}, bmp_{platform} {}

    Result init() noexcept override {
        if (ready_) {
            return {};
        }
        if (auto clocked = platform_.clock_init(); !clocked) {
            return clocked;
        }

        // Перше, що робимо, — гарантовано розмикаємо всі силові ключі.
        for (std::size_t i = 0; i < kDomains.size(); ++i) {
            platform_.pin_mode(kDomains[i].gate, PinMode::OutputPushPull);
            platform_.pin_write(kDomains[i].gate, !kDomains[i].gate_active_high);
            domain_on_[i] = false;
        }
        for (std::size_t i = 0; i < kLeds.size(); ++i) {
            apply_led(kLeds[i], false);
            led_state_[i] = LedState::Off;
        }

        // Виводи знеструмленого домену — в аналоговий режим, інакше давач
        // паразитно живиться через ESD-діоди ліній шини.
        platform_.pin_mode(kI2cScl, PinMode::Analog);
        platform_.pin_mode(kI2cSda, PinMode::Analog);
        platform_.pin_mode(kChargerStat, PinMode::InputPullUp);

        if (auto adc = platform_.adc_init(); !adc) {
            return adc;
        }

        bmp_.invalidate();
        ready_ = true;
        return {};
    }

    Result deinit() noexcept override {
        if (!ready_) {
            return {};
        }
        for (std::size_t i = 0; i < kDomains.size(); ++i) {
            (void)power_domain_set(static_cast<PowerDomain>(i), false);
        }
        for (std::size_t i = 0; i < kLeds.size(); ++i) {
            apply_led(kLeds[i], false);
            platform_.pin_mode(kLeds[i].pin, PinMode::Analog);
            led_state_[i] = LedState::Off;
        }
        platform_.adc_deinit();
        ready_ = false;
        return {};
    }

    Result led_set(LedId led, LedState state) noexcept override {
        if (index_of(led) >= kLeds.size()) {
            return fail(Status::InvalidParam);
        }
        if (!ready_) {
            return fail(Status::NotInitialized);
        }
        // Один запис у BSRR — операція атомарна, тож дозволена і в ISR.
        apply_led(kLeds[index_of(led)], state == LedState::On);
        led_state_[index_of(led)] = state;
        return {};
    }

    Result led_toggle(LedId led) noexcept override {
        if (index_of(led) >= kLeds.size()) {
            return fail(Status::InvalidParam);
        }
        // Стан беремо з тіньової копії: вивід із відкритим стоком читати марно.
        return led_set(led, led_state_[index_of(led)] == LedState::On ? LedState::Off
                                                                     : LedState::On);
    }

    Result power_domain_set(PowerDomain domain, bool enable) noexcept override {
        const std::size_t i = index_of(domain);
        if (i >= kDomains.size()) {
            return fail(Status::InvalidParam);
        }
        if (!ready_) {
            return fail(Status::NotInitialized);
        }
        if (platform_.in_isr()) {
            // Блокує на десятки мілісекунд — у перериванні заборонено.
            return fail(Status::Unsupported);
        }

        const DomainDesc& desc = kDomains[i];

        if (enable) {
            if (domain_on_[i]) {
                return {};
            }
            platform_.pin_write(desc.gate, desc.gate_active_high);
            // Плавний заряд блокувальних конденсаторів домену.
            platform_.delay(desc.settle);

            if (desc.owns_bus) {
                if (auto bus = platform_.i2c_init(); !bus) {
                    // Відкат: живлення не лишаємо ввімкненим при мертвій шині.
                    platform_.pin_write(desc.gate, !desc.gate_active_high);
                    return bus;
                }
                bmp_.invalidate();
            }
            domain_on_[i]    = true;
            domain_ready_[i] = platform_.tick();
            return {};
        }

        if (!domain_on_[i]) {
            return {};
        }
        if (desc.owns_bus) {
            // Спершу Hi-Z на лініях, і лише потім знімаємо живлення.
            platform_.i2c_deinit();
            platform_.pin_mode(kI2cScl, PinMode::Analog);
            platform_.pin_mode(kI2cSda, PinMode::Analog);
            bmp_.invalidate();
        }
        platform_.pin_write(desc.gate, !desc.gate_active_high);
        domain_on_[i] = false;
        return {};
    }

    std::expected<BatteryMetrics, Status> battery_metrics() noexcept override {
        if (!ready_) {
            return fail(Status::NotInitialized);
        }

        const auto raw_vref = platform_.adc_sample(kAdcChannelVrefint);
        if (!raw_vref) {
            return fail(raw_vref.error());
        }
        if (*raw_vref == 0) {
            // Опорне джерело не запустилося — рахувати немає від чого.
            return fail(Status::PowerFault);
        }
        const auto raw_vbat = platform_.adc_sample(kAdcChannelVbat);
        if (!raw_vbat) {
            return fail(raw_vbat.error());
        }

        // Живлення АЦП відновлюємо із заводської константи, а не припускаємо 3.3 В.
        const std::uint32_t vdda_mv = (kVrefintCalMv * platform_.vrefint_cal()) / *raw_vref;
        const std::uint32_t vbat_mv = (static_cast<std::uint32_t>(*raw_vbat) * vdda_mv *
                                       kVbatDivider) / kAdcFullScale;

        const BatteryMetrics metrics{
            .voltage_mv      = static_cast<std::uint16_t>(vbat_mv),
            .charge_percent  = charge_percent(vbat_mv),
            .is_charging     = !platform_.pin_read(kChargerStat),
            .is_critical_low = vbat_mv < kBatteryCriticalMv,
        };

        if (vbat_mv < kBatteryCutoffMv) {
            // Виміряли успішно, але це вже аварія живлення.
            return fail(Status::PowerFault);
        }
        return metrics;
    }

    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override {
        if (!ready_) {
            return fail(Status::NotInitialized);
        }
        if (platform_.in_isr()) {
            // Блокуючий обмін по I2C у перериванні зірвав би реальний час.
            return fail(Status::Unsupported);
        }
        const std::size_t sensors = index_of(PowerDomain::Sensors);
        if (!domain_on_[sensors]) {
            return fail(Status::NotInitialized);
        }

        if (const auto elapsed = platform_.tick() - domain_ready_[sensors];
            elapsed < kSensorWarmup) {
            platform_.delay(kSensorWarmup - elapsed);
        }

        // Шина спільна: транзакцію накриваємо м'ютексом самі.
        BusLock lock{platform_, kBusLockTimeout};
        if (!lock) {
            return fail(Status::Busy);
        }

        const auto climate = sht_.measure();
        if (!climate) {
            return fail(recover_if_bus_fault(climate.error()));
        }
        const auto pressure = bmp_.pressure_pa();
        if (!pressure) {
            return fail(recover_if_bus_fault(pressure.error()));
        }
        // Поза паспортним діапазоном давача (-40..+125 °C) — результат недійсний.
        if (climate->temperature_centi_c < -4000 || climate->temperature_centi_c > 12500) {
            return fail(recover_if_bus_fault(Status::BusFault));
        }

        return EnvironmentMetrics{
            .temperature_centi_c = climate->temperature_centi_c,
            .pressure_pa         = *pressure,
            .humidity_centi_pct  = climate->humidity_centi_pct,
        };
    }

    Result enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept override {
        if (!ready_) {
            return fail(Status::NotInitialized);
        }
        if (platform_.in_isr()) {
            return fail(Status::Unsupported);
        }

        // Спершу DMA й UART: зупинити тактування посеред кадру = втрата даних.
        if (auto flushed = platform_.flush_async_io(kFlushTimeout); !flushed) {
            return flushed;
        }

        (void)power_domain_set(PowerDomain::Sensors, false);
        if (mode == SleepMode::Deep) {
            (void)power_domain_set(PowerDomain::Radio, false);
            (void)power_domain_set(PowerDomain::Display, false);
            for (const LedDesc& led : kLeds) {
                apply_led(led, false);
                platform_.pin_mode(led.pin, PinMode::Analog);
            }
            platform_.adc_deinit();
        }

        Result slept = platform_.enter_stop(mode, timeout);

        if (mode == SleepMode::Deep) {
            // Після зупинки генератора тактування піднімається наново.
            if (auto clocked = platform_.clock_init(); !clocked) {
                return clocked;
            }
            if (auto adc = platform_.adc_init(); !adc) {
                return adc;
            }
            for (std::size_t i = 0; i < kLeds.size(); ++i) {
                apply_led(kLeds[i], led_state_[i] == LedState::On);
            }
        }
        return slept;
    }

    [[nodiscard]] std::chrono::milliseconds uptime() const noexcept override {
        return platform_.tick();
    }

    void delay(std::chrono::microseconds us) const noexcept override {
        platform_.delay(us);
    }

private:
    void apply_led(const LedDesc& desc, bool on) noexcept {
        if (desc.open_drain) {
            // Спільний анод: світимо, притискаючи катод до землі; гасимо — в Hi-Z.
            if (on) {
                platform_.pin_mode(desc.pin, PinMode::OutputOpenDrain);
                platform_.pin_write(desc.pin, false);
            } else {
                platform_.pin_mode(desc.pin, PinMode::Input);
            }
            return;
        }
        platform_.pin_mode(desc.pin, PinMode::OutputPushPull);
        platform_.pin_write(desc.pin, desc.active_high ? on : !on);
    }

    /**
     * Ведений, якого перервали посеред байта, тримає SDA у нулі. Дев'ять
     * тактів SCL дають йому доклацати транзакцію, далі формуємо STOP руками.
     */
    [[nodiscard]] Status recover_if_bus_fault(Status status) noexcept {
        if (status != Status::BusFault) {
            return status;
        }

        platform_.i2c_deinit();
        platform_.pin_mode(kI2cScl, PinMode::OutputOpenDrain);
        platform_.pin_write(kI2cScl, true);
        platform_.pin_mode(kI2cSda, PinMode::InputPullUp);

        for (int pulse = 0; pulse < 9 && !platform_.pin_read(kI2cSda); ++pulse) {
            platform_.pin_write(kI2cScl, false);
            platform_.delay(5us);
            platform_.pin_write(kI2cScl, true);
            platform_.delay(5us);
        }

        // STOP: фронт SDA 0→1 при високому SCL.
        platform_.pin_mode(kI2cSda, PinMode::OutputOpenDrain);
        platform_.pin_write(kI2cSda, false);
        platform_.delay(5us);
        platform_.pin_write(kI2cScl, true);
        platform_.delay(5us);
        platform_.pin_write(kI2cSda, true);
        platform_.delay(5us);

        (void)platform_.i2c_init();
        bmp_.invalidate();
        return Status::BusFault;
    }

    IPlatform&      platform_;
    detail::Sht3x   sht_;
    detail::Bmp280  bmp_;

    std::array<bool, 3>                      domain_on_{};
    std::array<std::chrono::milliseconds, 3> domain_ready_{};
    std::array<LedState, 3>                  led_state_{};
    bool                                     ready_{false};
};

} // namespace

std::unique_ptr<IBoardSupport> make_board(IPlatform& platform) {
    return std::make_unique<BoardImpl>(platform);
}

} // namespace bsp
