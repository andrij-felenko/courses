#include "Moc3063.hpp"
#include <utility>

Moc3063::Moc3063(const Moc3063Config& config) noexcept
    : config_(config), current_state_(LoadState::Disabled), is_initialized_(false) {
}

Moc3063::~Moc3063() noexcept {
    if (is_initialized_) {
        // Гарантоване вимкнення навантаження при виході з обережності
        (void)turnOff();
    }
}

Moc3063::Moc3063(Moc3063&& other) noexcept
    : config_(other.config_),
      current_state_(other.current_state_),
      is_initialized_(other.is_initialized_) {
    other.is_initialized_ = false;
    other.current_state_ = LoadState::Disabled;
}

Moc3063& Moc3063::operator=(Moc3063&& other) noexcept {
    if (this != &other) {
        if (is_initialized_) {
            (void)turnOff();
        }
        config_ = other.config_;
        current_state_ = other.current_state_;
        is_initialized_ = other.is_initialized_;

        other.is_initialized_ = false;
        other.current_state_ = LoadState::Disabled;
    }
    return *this;
}

Status Moc3063::init() noexcept {
    if (is_initialized_) {
        return Status::AlreadyInitialized;
    }

    if (config_.write_fn == nullptr || config_.init_fn == nullptr) {
        return Status::HardwareError;
    }

    // Визначаємо неактивний рівень GPIO, при якому світлодіод точно не горить
    LogicLevel inactive_level = (config_.active_level == ActiveLevel::ActiveHigh)
                                    ? LogicLevel::Low
                                    : LogicLevel::High;

    // Безпечна ініціалізація виводу: запис неактивного рівня до ввімкнення режимів Output
    if (!config_.init_fn(config_.pin, inactive_level)) {
        return Status::HardwareError;
    }

    is_initialized_ = true;

    // Встановлюємо початковий стан комутації
    return setState(config_.initial_state);
}

Status Moc3063::turnOn() noexcept {
    return setState(LoadState::Enabled);
}

Status Moc3063::turnOff() noexcept {
    return setState(LoadState::Disabled);
}

Status Moc3063::toggle() noexcept {
    if (!is_initialized_) {
        return Status::NotInitialized;
    }
    LoadState next_state = (current_state_ == LoadState::Enabled)
                               ? LoadState::Disabled
                               : LoadState::Enabled;
    return setState(next_state);
}

Status Moc3063::setState(LoadState state) noexcept {
    if (!is_initialized_) {
        return Status::NotInitialized;
    }

    LogicLevel pin_level = stateToLogicLevel(state);
    config_.write_fn(config_.pin, pin_level);

    current_state_ = state;
    return Status::Ok;
}

LoadState Moc3063::getState() const noexcept {
    return current_state_;
}

bool Moc3063::isEnabled() const noexcept {
    return current_state_ == LoadState::Enabled;
}

bool Moc3063::isInitialized() const noexcept {
    return is_initialized_;
}

uint8_t Moc3063::getPin() const noexcept {
    return config_.pin;
}

LogicLevel Moc3063::stateToLogicLevel(LoadState state) const noexcept {
    if (state == LoadState::Enabled) {
        return (config_.active_level == ActiveLevel::ActiveHigh)
                   ? LogicLevel::High
                   : LogicLevel::Low;
    } else {
        return (config_.active_level == ActiveLevel::ActiveHigh)
                   ? LogicLevel::Low
                   : LogicLevel::High;
    }
}
