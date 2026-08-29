// supervisor.hpp — політика виживання в полі.
//
// Один об'єкт тримає три незалежні загрози: перегрів, мороз і просадку шини
// під імпульсом передавача. Кожен перехід має гістерезис — інакше рівно на
// межі прилад почне клацати навантаженням щоцикла, а клацання силового
// ключа тут дорожче за сам перегрів.
//
// Передавач видається орендою (RadioLease) з деструктором. Забути звільнити
// його в сишному варіанті означало б лишити двоамперне навантаження ввімкненим
// на морозі — тут це неможливо навіть на шляху виходу через виняток.
#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>

namespace field {

// Пороги з паспорта виробу, не з голови: +85 °C — верхня межа промислового
// діапазону, 3.0 В — межа, за якою акумулятор вважається розрядженим.
struct Limits {
    static constexpr std::int16_t kThrottleOnC = 80;
    static constexpr std::int16_t kThrottleOffC = 65;
    static constexpr std::int16_t kCriticalOnC = 95;
    static constexpr std::int16_t kCriticalOffC = 85;
    static constexpr std::int16_t kChargeBlockC = 0;  // нижче нуля заряд літію заборонено
    static constexpr std::int16_t kChargeAllowC = 3;
    static constexpr std::int16_t kHeaterOnC = -10;
    static constexpr std::int16_t kHeaterOffC = 0;

    static constexpr std::uint16_t kShedMv = 3100;   // нижче — скидаємо навантаження
    static constexpr std::uint16_t kSupplyOkMv = 3300;
    static constexpr std::uint16_t kFloorMv = 3050;  // прогноз нижче — радіо не вмикаємо

    static constexpr std::uint16_t kRadioPulseMa = 2000;
    static constexpr std::uint16_t kColdRIntMohm = 300;
    static constexpr std::chrono::milliseconds kBlindLimit{5000};
};

// Обидва канали окремо необов'язкові: часткові дані теж корисні, і саме
// std::optional не дає прийняти «не виміряли» за нуль градусів.
struct Sample {
    std::optional<std::int16_t> temperatureC;
    std::optional<std::uint16_t> vbatMv;

    [[nodiscard]] bool blind() const noexcept { return !temperatureC && !vbatMv; }
};

enum class Thermal : std::uint8_t {
    Nominal = 0,
    Throttled,  // частота ядра поділена, радіо заборонене
    Critical    // усе, крім вимірювання, вимкнено
};

enum class Deny : std::uint8_t {
    Hot,
    Cold,
    Sag,   // прогнозована просадка нижче підлоги
    Blind  // невідомо, у якому ми середовищі
};

[[nodiscard]] std::string_view name(Deny reason) noexcept;

class Supervisor {
public:
    // Оренда передавача. Рухома, не копійована; деструктор гасить радіо
    // й на тій самій парі замірів уточнює внутрішній опір джерела.
    class RadioLease {
    public:
        RadioLease(RadioLease&& other) noexcept : owner_{other.owner_} { other.owner_ = nullptr; }
        RadioLease& operator=(RadioLease&& other) noexcept;
        RadioLease(const RadioLease&) = delete;
        RadioLease& operator=(const RadioLease&) = delete;
        ~RadioLease() { release(); }

        // Передавач могли зняти й без нас — кроком політики, через просадку.
        [[nodiscard]] bool live() const noexcept;
        void release() noexcept;

    private:
        friend class Supervisor;
        explicit RadioLease(Supervisor& owner) noexcept : owner_{&owner} {}
        Supervisor* owner_{nullptr};
    };

    // safeStart = true після Brownout або HardFault: піднімаємось одразу
    // зі зниженою частотою й без радіо, доки не побачимо здорове середовище.
    Supervisor(bool safeStart, std::chrono::milliseconds now);

    // Один замір середовища: NTC на PA0 і напруга акумулятора на PA1.
    [[nodiscard]] static Sample measure() noexcept;

    // Крок політики. Викликати з фіксованим періодом.
    void step(const Sample& sample, std::chrono::milliseconds now);

    [[nodiscard]] std::expected<RadioLease, Deny> requestRadio() noexcept;

    [[nodiscard]] Thermal thermal() const noexcept { return thermal_; }
    [[nodiscard]] std::int16_t lastTemperatureC() const noexcept { return lastTempC_; }
    [[nodiscard]] std::uint16_t idleMv() const noexcept { return idleMv_; }
    [[nodiscard]] std::uint32_t sagEvents() const noexcept { return sagEvents_; }
    [[nodiscard]] std::chrono::milliseconds uptime(std::chrono::milliseconds now) const noexcept {
        return now - startedAt_;
    }

private:
    void applyThermal(Thermal state) noexcept;
    void stepThermal(std::int16_t temperatureC) noexcept;
    void stepCold(const Sample& sample) noexcept;
    void stepSupply(std::uint16_t mv) noexcept;
    void releaseRadio() noexcept;

    Thermal thermal_{Thermal::Nominal};
    bool chargeBlocked_{true};  // доки не побачили температуру — заряд заборонено
    bool heaterOn_{false};
    bool blind_{true};
    std::chrono::milliseconds blindSince_{};
    std::chrono::milliseconds startedAt_{};

    std::uint16_t idleMv_{0};                        // напруга без навантаження
    std::optional<std::uint16_t> rIntMohm_;          // оцінка внутрішнього опору джерела
    std::uint32_t sagEvents_{0};
    std::int16_t lastTempC_{0};
};

}  // namespace field
