// supervisor.cpp — автомат станів нагляду за вхідним живленням.
#include "supervisor.hpp"

#include <utility>

namespace power {

std::string_view to_string(State state) noexcept
{
    switch (state) {
        case State::Off:        return "Off";
        case State::Settling:   return "Settling";
        case State::Running:    return "Running";
        case State::FaultUvlo:  return "FaultUvlo";
        case State::FaultOvlo:  return "FaultOvlo";
        case State::FaultEfuse: return "FaultEfuse";
        case State::LockedOut:  return "LockedOut";
    }
    return "?";
}

std::string_view to_string(Fault fault) noexcept
{
    switch (fault) {
        case Fault::NotReady:     return "живлення ще не дозволене";
        case Fault::Undervoltage: return "просідання нижче UVLO";
        case Fault::Overvoltage:  return "перенапруга вище OVLO";
        case Fault::EfuseTrip:    return "спрацював eFuse";
        case Fault::LockedOut:    return "засув після серії аварій";
    }
    return "невідома причина";
}

void Window::validate() const
{
    // Пороги мусять іти зростаючим рядом, інакше гістерезис вивернеться навиворіт
    // і перший же дотик до порога заганяє ключ у брязкіт.
    const bool ordered = uvlo_trip < uvlo_clear && uvlo_clear < ovlo_clear && ovlo_clear < ovlo_trip;
    if (!ordered) throw std::invalid_argument{"пороги вікна безпеки задані не по зростанню"};
}

Supervisor::Supervisor(Config config, SwitchDriver driver)
    : config_{config}
    , driver_{std::move(driver)}
    , filter_{config.filter_shift}
{
    if (!driver_) throw std::invalid_argument{"не задано драйвер ключа живлення"};
    if (config_.confirm_samples == 0 || config_.settle_samples == 0) {
        throw std::invalid_argument{"підтвердження й витримка не можуть бути нульовими"};
    }
    config_.window.validate();

    // Поки напруга не виміряна, дозволяти живлення нема підстав.
    enabled_ = true;
    set_output(false);
}

Supervisor::~Supervisor()
{
    // Наглядач пішов — ключ розімкнено. Виняток із драйвера тут ловимо: кидати
    // з деструктора не можна, а лишати вихід під напругою тим паче.
    try {
        set_output(false);
    } catch (...) {
    }
}

void Supervisor::set_output(bool on)
{
    if (enabled_ == on) return;
    enabled_ = on;
    driver_(on);
}

bool Supervisor::inside_window() const noexcept
{
    return voltage_ >= config_.window.uvlo_clear && voltage_ <= config_.window.ovlo_clear;
}

void Supervisor::enter_fault(State fault, std::chrono::milliseconds now)
{
    set_output(false);
    confirm_count_ = 0;
    settle_count_ = 0;
    pending_fault_ = State::Off;
    last_fault_ = now;

    switch (fault) {
        case State::FaultUvlo:  ++stats_.uvlo_events;  break;
        case State::FaultOvlo:  ++stats_.ovlo_events;  break;
        case State::FaultEfuse: ++stats_.efuse_events; break;
        default: break;
    }

    if (config_.retry.limit != 0 && retries_used_ >= config_.retry.limit) {
        // Повтори вичерпано: це вже не перехідний процес, а несправність.
        state_ = State::LockedOut;
        ++stats_.lockouts;
        return;
    }

    ++retries_used_;
    state_ = fault;
    retry_at_ = now + config_.retry.delay;
}

void Supervisor::on_sample(std::uint16_t adc_code, std::chrono::milliseconds now)
{
    voltage_ = config_.divider.bus(filter_(adc_code));

    ++stats_.samples;
    stats_.v_min = std::min(stats_.v_min, voltage_);
    stats_.v_max = std::max(stats_.v_max, voltage_);

    // Апаратна аварія б'є будь-який стан, крім засува: eFuse уже розімкнув вихід
    // сам, прошивці лишається не заперечувати й зафіксувати подію.
    if (efuse_flag_.exchange(false, std::memory_order_acquire) && state_ != State::LockedOut) {
        enter_fault(State::FaultEfuse, now);
        return;
    }

    switch (state_) {
        case State::Off:
            if (inside_window()) {
                settle_count_ = 0;
                state_ = State::Settling;
            }
            break;

        case State::Settling:
            if (!inside_window()) {
                settle_count_ = 0;
                state_ = State::Off;
                break;
            }
            if (++settle_count_ >= config_.settle_samples) {
                settle_count_ = 0;
                confirm_count_ = 0;
                set_output(true);
                ++stats_.starts;
                state_ = State::Running;
            }
            break;

        case State::Running: {
            State fault = State::Off;
            if (voltage_ < config_.window.uvlo_trip)      fault = State::FaultUvlo;
            else if (voltage_ > config_.window.ovlo_trip) fault = State::FaultOvlo;

            if (fault == State::Off) {
                confirm_count_ = 0;
                pending_fault_ = State::Off;
                // Довга тиша означає, що аварії були поодинокі, а не серія.
                if (retries_used_ != 0 && now - last_fault_ >= config_.retry.window) {
                    retries_used_ = 0;
                }
                break;
            }

            // Одна вибірка нічого не доводить: голку від комутації сусіднього
            // навантаження фільтр не встигає з'їсти цілком.
            if (fault != pending_fault_) {
                pending_fault_ = fault;
                confirm_count_ = 0;
            }
            if (++confirm_count_ >= config_.confirm_samples) {
                enter_fault(fault, now);
            }
            break;
        }

        case State::FaultUvlo:
        case State::FaultOvlo:
        case State::FaultEfuse:
            if (now >= retry_at_) {
                state_ = State::Off;  // далі звичайний шлях Off → Settling → Running
            }
            break;

        case State::LockedOut:
            break;  // виходу нема: лише clear_lockout()
    }
}

std::expected<Millivolts, Fault> Supervisor::reading() const noexcept
{
    switch (state_) {
        case State::Running:    return voltage_;
        case State::FaultUvlo:  return std::unexpected{Fault::Undervoltage};
        case State::FaultOvlo:  return std::unexpected{Fault::Overvoltage};
        case State::FaultEfuse: return std::unexpected{Fault::EfuseTrip};
        case State::LockedOut:  return std::unexpected{Fault::LockedOut};
        case State::Off:
        case State::Settling:   return std::unexpected{Fault::NotReady};
    }
    return std::unexpected{Fault::NotReady};
}

bool Supervisor::clear_lockout(std::chrono::milliseconds now) noexcept
{
    if (state_ != State::LockedOut) return false;
    retries_used_ = 0;
    confirm_count_ = 0;
    settle_count_ = 0;
    pending_fault_ = State::Off;
    last_fault_ = now;
    state_ = State::Off;
    return true;
}

}  // namespace power
