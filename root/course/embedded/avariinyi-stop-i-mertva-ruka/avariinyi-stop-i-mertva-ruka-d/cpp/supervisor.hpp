#pragma once

// Наглядач контуру: зводить докупи діагностику каналів E-Stop, кнопку
// мертвої руки та петлю EDM і керує котушками силових контакторів.

#include <string_view>

#include "channel_monitor.hpp"
#include "enabling_device.hpp"
#include "safety_hal.hpp"

namespace safety {

enum class State : std::uint8_t {
    Idle = 0,              // безпечний стан після ввімкнення живлення
    Running,
    StoppedEstop,          // натиснуто грибок або розірвано контур
    StoppedEnable,         // кнопка мертвої руки не в Позиції 2
    FaultShortToSupply,
    FaultCrossCircuit,
    FaultDiscordance,
    FaultEnableContacts,
    FaultEdm               // контактор не відпустив або обірвано петлю
};

constexpr bool isFault(State state) noexcept
{
    return state >= State::FaultShortToSupply;
}

std::string_view describe(State state) noexcept;

class Supervisor {
public:
    static constexpr Millis kEdmCloseLimit{250};   // NC мусять зійтися після знеструмлення
    static constexpr Millis kEdmOpenLimit{250};    // і розійтися після втягування

    // Конструктор ставить контур у безпечний стан і знімає залиплі помилки:
    // це дія обслуговування, а не автоматичне скидання.
    explicit Supervisor(Hal& hal);

    // Викликати з головного циклу. Період — одиниці мілісекунд.
    void poll();

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool outputsOn() const noexcept { return contactorsOn_; }

private:
    void deenergize();
    void superviseEdm(Millis dt);

    Hal&           hal_;
    ChannelMonitor channels_;
    EnablingDevice enabling_;

    State  state_{State::Idle};
    bool   contactorsOn_{};
    bool   edmWatch_{};      // чекаємо, поки дзеркальні контакти перекинуться
    bool   resetPrev_{};
    Millis edmTimer_{};
    Millis last_{};
};

}  // namespace safety
