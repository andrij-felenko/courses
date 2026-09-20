#include "g3mb202p.hpp"
#include <iostream>

namespace drivers {

G3MB202P::G3MB202P(GpioConfig gpio_cfg, SafetyConfig safety_cfg)
    : gpio_cfg_(gpio_cfg), safety_cfg_(safety_cfg) {}

G3MB202P::~G3MB202P() {
    if (is_initialized_) {
        // Задля безпеки переводимо реле у вимкнений стан при знищенні об'єкта
        apply_state(RelayState::Off, true);
    }
}

bool G3MB202P::init() {
    // Ініціалізація режиму GPIO піна (Output)
    std::cout << "[G3MB-202P] Ініціалізація GPIO піна " << static_cast<int>(gpio_cfg_.pin_number)
              << " у режим OUTPUT...\n";

    is_initialized_ = true;

    // Встановлюємо початковий стан "Вимкнено" без урахування часового обмеження
    apply_state(RelayState::Off, true);
    return true;
}

bool G3MB202P::can_switch() const noexcept {
    if (last_switch_time_ == clock::time_point::min()) {
        return true;
    }
    const auto now = clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_switch_time_);
    return elapsed >= safety_cfg_.min_switch_interval;
}

std::chrono::milliseconds G3MB202P::time_until_next_switch() const noexcept {
    if (can_switch()) {
        return std::chrono::milliseconds(0);
    }
    const auto now = clock::now();
    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_switch_time_);
    return safety_cfg_.min_switch_interval - elapsed;
}

SwitchResult G3MB202P::turn_on(bool force) {
    return apply_state(RelayState::On, force);
}

SwitchResult G3MB202P::turn_off(bool force) {
    return apply_state(RelayState::Off, force);
}

SwitchResult G3MB202P::toggle() {
    const auto next_state = (current_state_ == RelayState::On) ? RelayState::Off : RelayState::On;
    return apply_state(next_state, false);
}

SwitchResult G3MB202P::apply_state(RelayState new_state, bool force) {
    if (!is_initialized_) {
        std::cerr << "[G3MB-202P] Помилка: Драйвер не ініціалізовано!\n";
        return SwitchResult::Throttled;
    }

    if (current_state_ == new_state) {
        return SwitchResult::AlreadyInState;
    }

    if (!force && !can_switch()) {
        const auto wait_ms = time_until_next_switch().count();
        std::cout << "[G3MB-202P] Обмеження частоти: занадто швидка комутація! Зачекайте ще "
                  << wait_ms << " мс.\n";
        return SwitchResult::Throttled;
    }

    // Визначаємо фізичний рівень на піні залежно від активного рівня
    const bool raw_level = (new_state == RelayState::On)
                           ? (gpio_cfg_.active_level == LogicLevel::ActiveHigh)
                           : (gpio_cfg_.active_level != LogicLevel::ActiveHigh);

    write_pin_hardware(raw_level);

    current_state_ = new_state;
    last_switch_time_ = clock::now();

    std::cout << "[G3MB-202P] Пін " << static_cast<int>(gpio_cfg_.pin_number)
              << " -> " << (raw_level ? "HIGH" : "LOW")
              << " | Навантаження 240 В: "
              << (current_state_ == RelayState::On ? "УВІМКНЕНО" : "ВИМКНЕНО") << "\n";

    return SwitchResult::Success;
}

void G3MB202P::write_pin_hardware(bool level) {
    // Емуляція запису сигналу у регістр GPIO мікроконтролера
    (void)level;
}

} // namespace drivers
