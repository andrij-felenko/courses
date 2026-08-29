#pragma once

#include <cstdint>
#include <string_view>

#include "evse/board.hpp"
#include "evse/units.hpp"

namespace evse::patterns {

/*
 * Патерн 1: вкладений switch-case. Найкоротший шлях від діаграми станів до
 * робочого коду. Компілятор згортає плоский switch за enum class у таблицю
 * переходів асемблера (TBB/TBH на Cortex-M): ні непрямих викликів, ні таблиць
 * у RAM, один байт стану.
 *
 * Плата за це — дії входу й виходу доводиться виписувати вручну на кожному
 * переході. Нижче на них припадає більша частина коду, і саме там ховається
 * найтиповіша помилка патерну: забуте розмикання реле в одній із гілок.
 */

enum class SwitchState : std::uint8_t { Standby, Connected, Charging, Fault };

enum class SwitchEvent : std::uint8_t {
    PlugIn,
    AuthSuccess,
    ChargeRequest,
    Unplug,
    Overcurrent,
    ResetButton
};

[[nodiscard]] constexpr std::string_view name(SwitchState s) noexcept
{
    switch (s) {
        case SwitchState::Standby:   return "STANDBY";
        case SwitchState::Connected: return "CONNECTED";
        case SwitchState::Charging:  return "CHARGING";
        default:                     return "FAULT";
    }
}

template <Board B>
class SwitchFsm {
public:
    explicit SwitchFsm(B& board, Amperes limit = Amperes{32}) noexcept
        : board_{board}, limit_{limit}
    {
        enterStandby();
    }

    [[nodiscard]] SwitchState state() const noexcept { return state_; }
    [[nodiscard]] bool        authorized() const noexcept { return authorized_; }

    void dispatch(SwitchEvent event)
    {
        switch (state_) {
            case SwitchState::Standby:
                switch (event) {
                    case SwitchEvent::PlugIn:      enterConnected(); break;
                    case SwitchEvent::Overcurrent: enterFault();     break;
                    default:                                         break;
                }
                break;

            case SwitchState::Connected:
                switch (event) {
                    case SwitchEvent::AuthSuccess:
                        authorized_ = true;
                        break;
                    case SwitchEvent::ChargeRequest:
                        if (authorized_) {
                            enterCharging();
                        }
                        break;
                    case SwitchEvent::Unplug:      enterStandby(); break;
                    case SwitchEvent::Overcurrent: enterFault();   break;
                    default:                                       break;
                }
                break;

            case SwitchState::Charging:
                switch (event) {
                    /* Кожна гілка виходу з CHARGING зобов'язана розімкнути
                     * реле — тут це роблять функції входу наступного стану. */
                    case SwitchEvent::PlugIn:      enterConnected(); break;
                    case SwitchEvent::Unplug:      enterStandby();   break;
                    case SwitchEvent::Overcurrent: enterFault();     break;
                    default:                                         break;
                }
                break;

            case SwitchState::Fault:
                if (event == SwitchEvent::ResetButton) {
                    enterStandby();
                }
                break;
        }
    }

private:
    void enterStandby()
    {
        board_.setRelay(false);
        board_.setLock(false);
        board_.setPilotDuty(Duty::steadyHigh());
        setLeds(true, false, false);
        authorized_ = false;
        state_      = SwitchState::Standby;
    }

    void enterConnected()
    {
        board_.setRelay(false);
        board_.setLock(true);
        board_.setPilotDuty(Duty::fromCurrent(limit_));
        setLeds(true, false, false);
        state_ = SwitchState::Connected;
    }

    void enterCharging()
    {
        board_.setRelay(true);
        setLeds(false, true, false);
        state_ = SwitchState::Charging;
    }

    void enterFault()
    {
        board_.setRelay(false);
        board_.forcePilotLow();
        board_.setLock(false);
        setLeds(false, false, true);
        authorized_ = false;
        state_      = SwitchState::Fault;
    }

    void setLeds(bool green, bool blue, bool red)
    {
        board_.setLed(Led::Green, green);
        board_.setLed(Led::Blue, blue);
        board_.setLed(Led::Red, red);
    }

    B&          board_;
    Amperes     limit_;
    SwitchState state_{SwitchState::Standby};
    bool        authorized_{false};
};

} // namespace evse::patterns
