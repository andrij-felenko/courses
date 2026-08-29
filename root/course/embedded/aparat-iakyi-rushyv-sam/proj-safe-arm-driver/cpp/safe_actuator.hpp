#pragma once

#include "hw_platform.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <expected>

namespace safety {

using namespace std::chrono_literals;

enum class State : std::uint8_t {
    Disarmed = 0,  // сила знята, помпа стоїть, ШІМ у нулі
    ArmRequested,  // запит із валідним токеном прийнято
    PreArmCheck,   // самодіагностика перед подачею сили
    Armed,         // робочий режим
    Fault          // аварія; вихід — лише повний перезапуск
};

enum class Fault : std::uint8_t {
    BadToken = 1,    // запит без валідного токена
    Sequence,        // виклик у неприпустимому стані
    ArmTimeout,      // послідовність узяття під силу не завершилась
    Voltage,         // напруга батареї поза вікном
    OverTemperature, // перегрів силового каскаду
    OverCurrent,     // спрацював компаратор струму
    EmergencyStop,   // натиснуто аварійну зупинку
    HeartbeatStall   // цикл спізнився, меандр розірвано
};

struct Config {
    static constexpr std::uint16_t pwmMaxDuty = 1000;
    static constexpr std::uint16_t minVoltageMv = 11000;
    static constexpr std::uint16_t maxVoltageMv = 14500;

    // Півперіод меандру: 500 мкс дають 1 кГц на виводі помпи.
    static constexpr std::chrono::microseconds heartbeatHalfPeriod = 500us;
    // Найдовша пауза, яку ще переживає фільтр помпи заряду.
    static constexpr std::chrono::microseconds heartbeatStall = 1500us;
    // Час на всю послідовність узяття під силу.
    static constexpr std::chrono::microseconds armTimeout = 200ms;
    // Вікно сторожа: довше за цикл, коротше за вибіг мотора.
    static constexpr std::chrono::milliseconds watchdogWindow = 50ms;
};

// Токен запиту окремим типом: випадкове ціле в цей параметр не заїде.
class ArmToken {
public:
    explicit constexpr ArmToken(std::uint32_t value) noexcept : value_{value} {}
    [[nodiscard]] constexpr std::uint32_t value() const noexcept {
        return value_;
    }

private:
    std::uint32_t value_;
};

inline constexpr ArmToken kArmToken{0x5A3C96E1U};

enum class Checkpoint : std::uint8_t { Estop = 1, Limits, State, Output };

/*
 * Рахівниця чекпойнтів циклу валідації. Сторожа годує ДЕСТРУКТОР — і лише
 * тоді, коли всі чотири рубежі пройдено в правильному порядку. Вийти з циклу
 * повз цю перевірку не можна навіть через ранній return.
 */
template <HardwarePlatform Platform>
class WatchdogCycle {
public:
    explicit WatchdogCycle(Platform &hw) noexcept : hw_{hw} {}

    WatchdogCycle(const WatchdogCycle &) = delete;
    WatchdogCycle &operator=(const WatchdogCycle &) = delete;

    ~WatchdogCycle() {
        if (passed_ == static_cast<std::uint8_t>(Checkpoint::Output)) {
            hw_.feedWatchdog();
        }
    }

    void pass(Checkpoint checkpoint) noexcept {
        const auto ordinal = static_cast<std::uint8_t>(checkpoint);
        passed_ = (ordinal == passed_ + 1) ? ordinal : broken;
    }

private:
    static constexpr std::uint8_t broken = 0xFF;

    Platform &hw_;
    std::uint8_t passed_{0};
};

template <HardwarePlatform Platform>
class SafeActuator {
public:
    explicit SafeActuator(Platform &hw) noexcept : hw_{hw} {
        // Виходи в безпечний нуль ще до того, як конструктор поверне
        // керування: об'єкт не існує в стані «виходи невідомі».
        hw_.setPwmDuty(0);
        hw_.writeHeartbeat(false);
    }

    SafeActuator(const SafeActuator &) = delete;
    SafeActuator &operator=(const SafeActuator &) = delete;

    // Запит на взяття під силу. Хибний токен або виклик не з Disarmed —
    // це порушення протоколу, тож відповідь не «ні», а аварія.
    [[nodiscard]] std::expected<void, Fault> requestArm(ArmToken token) noexcept {
        if (token.value() != kArmToken.value()) {
            return fail(Fault::BadToken);
        }
        if (state_ != State::Disarmed) {
            return fail(Fault::Sequence);
        }
        state_ = State::ArmRequested;
        armRequestedAt_ = hw_.now();
        return {};
    }

    // Штатне зняття сили. Стан Fault не скидає — з нього виходу немає.
    void disarm() noexcept {
        pwm_ = 0;
        heartbeatLevel_ = false;
        if (state_ != State::Fault) {
            state_ = State::Disarmed;
        }
        applyOutputs();
    }

    // Один цикл валідації. Викликати не рідше, ніж раз на півперіод меандру.
    [[nodiscard]] std::expected<void, Fault> update(std::uint16_t targetPwm) noexcept {
        WatchdogCycle cycle{hw_};
        const auto now = hw_.now();

        // Рубіж 1. Аварійна зупинка без фільтра деренчання на небезпечному
        // напрямку: активний рівень діє з першого ж зчитування.
        if (hw_.estopActive()) {
            (void)fail(Fault::EmergencyStop);
        }
        cycle.pass(Checkpoint::Estop);

        // Рубіж 2. Межі живлення й силового каскаду — щоцикла, бо батарея
        // просідає саме під навантаженням, а не перед стартом.
        const Limits limits = readLimits();
        cycle.pass(Checkpoint::Limits);

        // Рубіж 3. Автомат станів.
        step(now, limits, targetPwm);
        cycle.pass(Checkpoint::State);

        // Рубіж 4. Виходи.
        applyOutputs();
        cycle.pass(Checkpoint::Output);

        // Годування сторожа зробить деструктор cycle — після обчислення
        // результату й лише за повного набору чекпойнтів.
        if (state_ == State::Fault) {
            return std::unexpected{fault_};
        }
        return {};
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool armed() const noexcept { return state_ == State::Armed; }
    [[nodiscard]] std::expected<void, Fault> health() const noexcept {
        if (state_ == State::Fault) {
            return std::unexpected{fault_};
        }
        return {};
    }

private:
    struct Limits {
        std::uint16_t voltageMv;
        bool overTemperature;
        bool overCurrent;
        bool ok;
    };

    [[nodiscard]] Limits readLimits() noexcept {
        Limits limits{hw_.supplyVoltageMv(), hw_.overTemperature(),
                      hw_.overCurrent(), false};
        limits.ok = limits.voltageMv >= Config::minVoltageMv &&
                    limits.voltageMv <= Config::maxVoltageMv &&
                    !limits.overTemperature && !limits.overCurrent;
        return limits;
    }

    [[nodiscard]] static Fault limitsFault(const Limits &limits) noexcept {
        if (limits.overCurrent) {
            return Fault::OverCurrent;
        }
        if (limits.overTemperature) {
            return Fault::OverTemperature;
        }
        return Fault::Voltage;
    }

    // Перша причина — головна: діагностика має показати, що зламалося
    // першим, а не що впало останнім.
    std::unexpected<Fault> fail(Fault reason) noexcept {
        if (state_ != State::Fault) {
            fault_ = reason;
        }
        state_ = State::Fault;
        pwm_ = 0;
        heartbeatLevel_ = false;
        return std::unexpected{fault_};
    }

    void step(std::chrono::microseconds now, const Limits &limits,
              std::uint16_t targetPwm) noexcept {
        switch (state_) {
        case State::Disarmed:
            pwm_ = 0;
            heartbeatLevel_ = false;
            break;

        case State::ArmRequested:
            if (now - armRequestedAt_ > Config::armTimeout) {
                (void)fail(Fault::ArmTimeout);
            } else {
                state_ = State::PreArmCheck;
            }
            break;

        case State::PreArmCheck:
            if (now - armRequestedAt_ > Config::armTimeout) {
                (void)fail(Fault::ArmTimeout);
            } else if (!limits.ok) {
                (void)fail(limitsFault(limits));
            } else {
                state_ = State::Armed;
                pwm_ = 0;
                // Меандр стартує з нуля, ШІМ теж: сила з'являється на
                // ключі раніше, ніж на моторі.
                heartbeatLevel_ = false;
                lastToggleAt_ = now;
            }
            break;

        case State::Armed:
            if (!limits.ok) {
                (void)fail(limitsFault(limits));
                break;
            }
            driveHeartbeat(now);
            if (state_ != State::Armed) {
                break; // серцебиття зірвалося, стан уже Fault
            }
            pwm_ = std::min(targetPwm, Config::pwmMaxDuty);
            break;

        case State::Fault:
            // Виходу з аварії немає: лише повний перезапуск контролера.
            (void)fail(Fault::Sequence);
            break;
        }
    }

    // Фаза меандру перемикається за часом, а не за кількістю викликів:
    // прив'язка до тактів циклу зробила б частоту помпи заручником джитера.
    void driveHeartbeat(std::chrono::microseconds now) noexcept {
        const auto elapsed = now - lastToggleAt_;

        if (elapsed >= Config::heartbeatStall) {
            // Цикл спізнився так, що фільтр помпи вже просів; ключ
            // розімкнувся сам, і меандр більше нічого не рятує.
            (void)fail(Fault::HeartbeatStall);
            return;
        }

        if (elapsed >= Config::heartbeatHalfPeriod) {
            heartbeatLevel_ = !heartbeatLevel_;
            lastToggleAt_ = now;
        }
    }

    // Єдине місце драйвера, що торкається виходів.
    void applyOutputs() noexcept {
        if (state_ == State::Armed) {
            hw_.writeHeartbeat(heartbeatLevel_);
            hw_.setPwmDuty(pwm_);
        } else {
            // Спершу знімаємо силу, потім дозвіл: зворотний порядок лишив
            // би вікно, у якому ШІМ ще котиться на живому ключі.
            hw_.setPwmDuty(0);
            hw_.writeHeartbeat(false);
        }
    }

    Platform &hw_;
    State state_{State::Disarmed};
    // Причина читається лише в стані Fault, тож окремого «None» у переліку
    // немає: недосяжного значення в типі краще не заводити.
    Fault fault_{Fault::Sequence};
    std::chrono::microseconds armRequestedAt_{0};
    std::chrono::microseconds lastToggleAt_{0};
    std::uint16_t pwm_{0};
    bool heartbeatLevel_{false};
};

} // namespace safety
