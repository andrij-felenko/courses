#include "arbiter.hpp"

namespace autopilot::failsafe {
namespace {

using namespace std::chrono_literals;

/* ---------------------------------------------------------------------
 * Таблиця пріоритетів. Правило спрацьовує, коли всі біти require
 * підтверджені й жодного з forbid немає; перше збіжне дає дію, тож
 * порядок рядків і є ієрархією. forbid потрібен через GNSS: майже кожна
 * відмова має дві відповіді — з супутниками повертаємося, без них сідаємо.
 * ------------------------------------------------------------------- */
struct Rule {
    std::uint32_t require;
    std::uint32_t forbid;
    Action action;
};

constexpr std::array kMatrix{
    // 1. Орієнтація втрачена: керувати нічим
    Rule{bit(Fault::AttitudeLoss), 0u, Action::Terminate},
    // 2. Відмова приводу: тяги вистачає на спуск, не на маршрут
    Rule{bit(Fault::Actuator), 0u, Action::Land},
    // 3. Критичний розряд: енергії на повернення немає
    Rule{bit(Fault::BatteryCrit), 0u, Action::Land},
    // 4-5. Геозона: назад за навігацією або вниз на межі
    Rule{bit(Fault::Geofence), bit(Fault::GnssGlitch), Action::ReturnToLaunch},
    Rule{bit(Fault::Geofence), 0u, Action::Land},
    // 6-7. Перший поріг батареї: ще встигаємо додому
    Rule{bit(Fault::BatteryLow), bit(Fault::GnssGlitch), Action::ReturnToLaunch},
    Rule{bit(Fault::BatteryLow), 0u, Action::Land},
    // 8-9. Втрата пульта: апарат лишився без оператора
    Rule{bit(Fault::RcLost), bit(Fault::GnssGlitch), Action::ReturnToLaunch},
    Rule{bit(Fault::RcLost), 0u, Action::Land},
    // 10. Самотній збій GNSS: пульт у руках, тримаємо висоту
    Rule{bit(Fault::GnssGlitch), 0u, Action::AltHold},
    // 11. Немає телеметрії — лише сигнал оператору
    Rule{bit(Fault::GcsLost), 0u, Action::Warn},
    // 12. Порожня вимога збігається завжди
    Rule{0u, 0u, Action::None},
};

} // namespace

Config Config::defaults() noexcept {
    Config cfg{};
    cfg.debounce[index(Fault::RcLost)]       = 1500ms;
    cfg.debounce[index(Fault::GcsLost)]      = 5000ms;
    cfg.debounce[index(Fault::GnssGlitch)]   = 3000ms;
    cfg.debounce[index(Fault::BatteryLow)]   = 1000ms;
    cfg.debounce[index(Fault::BatteryCrit)]  = 1000ms;
    cfg.debounce[index(Fault::Geofence)]     = 500ms;
    cfg.debounce[index(Fault::Actuator)]     = 0ms; // без фільтрації
    cfg.debounce[index(Fault::AttitudeLoss)] = 0ms; // без фільтрації
    cfg.actionHold = 500ms;
    return cfg;
}

Action decide(const FaultMask& confirmed) noexcept {
    const auto bits = static_cast<std::uint32_t>(confirmed.to_ulong());
    for (const Rule& r : kMatrix) {
        if ((bits & r.require) == r.require && (bits & r.forbid) == 0u) {
            return r.action;
        }
    }
    return Action::None; // недосяжно: останнє правило порожнє
}

void Arbiter::resetTimers() noexcept {
    since_.fill(std::nullopt);
    confirmed_.reset();
}

void Arbiter::preflightDone(Millis now) noexcept {
    resetTimers();
    action_ = Action::None;
    action_since_ = now;
    armed_ = true;
}

void Arbiter::disarm() noexcept {
    resetTimers();
    action_ = Action::None;
    armed_ = false;
}

bool Arbiter::operatorAck(Millis now) noexcept {
    if (action_ == Action::Terminate) {
        return false; // з термінації в польоті виходу немає
    }
    action_ = Action::None;
    action_since_ = now;
    // Підтверджену маску лишаємо: якщо відмова жива, наступний такт
    // підніме ту саму дію негайно — і це правильно.
    return true;
}

Action Arbiter::update(const FaultMask& raw, Millis now) noexcept {
    if (!armed_) {
        // Фаза калібрування: сенсори ще брешуть, рішень не приймаємо.
        resetTimers();
        action_ = Action::None;
        return Action::None;
    }

    // 1. Часова фільтрація: аномалія стає відмовою, лише переживши поріг.
    for (std::size_t i = 0; i < kFaultCount; ++i) {
        if (raw.test(i)) {
            if (!since_[i].has_value()) {
                since_[i] = now;
            }
            if (now - *since_[i] >= cfg_.debounce[i]) {
                confirmed_.set(i);
            }
        } else {
            since_[i].reset();
            confirmed_.reset(i); // канал ожив — відмова знята
        }
    }

    // 2. Арбітраж: суперечливі вимоги зводить одна таблиця.
    const Action want = decide(confirmed_);

    // 3. Одностороннє підвищення суворості. Назад — лише за командою
    //    оператора або після зняття з охорони: інакше апарат вискакував би
    //    з посадки щоразу, коли напруга підстрибне на десяток мілівольт.
    if (want <= action_) {
        return action_;
    }

    // 4. Квант часу між змінами дії, щоб контури PID не діставали
    //    суперечливих команд поспіль. Термінація не чекає нікого; так само
    //    не чекає перший вихід зі штатного режиму.
    if (want != Action::Terminate && action_ != Action::None &&
        now - action_since_ < cfg_.actionHold) {
        return action_;
    }

    action_ = want;
    action_since_ = now;
    return action_;
}

} // namespace autopilot::failsafe
