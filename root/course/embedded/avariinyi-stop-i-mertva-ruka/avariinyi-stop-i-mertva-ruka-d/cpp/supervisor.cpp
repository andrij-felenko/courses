#include "supervisor.hpp"

namespace safety {

std::string_view describe(State state) noexcept
{
    switch (state) {
    case State::Idle:                return "очікування пуску";
    case State::Running:             return "РОБОТА";
    case State::StoppedEstop:        return "стоп: контур E-Stop розірвано";
    case State::StoppedEnable:       return "стоп: немає дозволу мертвої руки";
    case State::FaultShortToSupply:  return "ПОМИЛКА: замикання лінії на +24 В";
    case State::FaultCrossCircuit:   return "ПОМИЛКА: міжканальне замикання";
    case State::FaultDiscordance:    return "ПОМИЛКА: розбіжність каналів E-Stop";
    case State::FaultEnableContacts: return "ПОМИЛКА: розбіжність контактів дозволу";
    case State::FaultEdm:            return "ПОМИЛКА: контактор не відпустив (EDM)";
    }
    return "?";
}

Supervisor::Supervisor(Hal& hal)
    : hal_{hal}, channels_{hal}, enabling_{hal}, last_{hal.now()}
{
    hal_.setContactors(false);
    hal_.setLamp(false);
    hal_.setBuzzer(false);
}

// Зупинка Категорії 0: струм із котушок знімається негайно, зворотні
// пружини розводять силові контакти. Одразу починаємо стежити за петлею.
void Supervisor::deenergize()
{
    if (!contactorsOn_) {
        return;
    }
    hal_.setContactors(false);
    contactorsOn_ = false;
    edmWatch_ = true;
    edmTimer_ = Millis{0};
}

// Дзеркальні контакти мусять перекинутися слідом за котушками за час
// механіки. Не перекинулися — силовий контакт зварився дугою або обірвано
// діагностичний шлейф.
void Supervisor::superviseEdm(Millis dt)
{
    if (!edmWatch_) {
        return;
    }

    const bool expected = !contactorsOn_;
    if (hal_.readEdmLoop() == expected) {
        edmWatch_ = false;
        edmTimer_ = Millis{0};
        return;
    }

    edmTimer_ += dt;
    if (edmTimer_ >= (contactorsOn_ ? kEdmOpenLimit : kEdmCloseLimit)) {
        edmWatch_ = false;
        state_ = State::FaultEdm;
        hal_.setContactors(false);
        contactorsOn_ = false;
    }
}

void Supervisor::poll()
{
    const Millis now = hal_.now();
    const Millis dt = now - last_;
    last_ = now;

    const std::expected<bool, LineFault> channels = channels_.update(dt);
    const std::expected<Grip, EnableFault> grip = enabling_.update(dt);

    const Indicators lights = enabling_.indicators();
    hal_.setLamp(lights.lamp);
    hal_.setBuzzer(lights.buzzer);

    if (!isFault(state_)) {
        if (!channels) {
            switch (channels.error()) {
            case LineFault::ShortToSupply: state_ = State::FaultShortToSupply; break;
            case LineFault::CrossCircuit:  state_ = State::FaultCrossCircuit;  break;
            case LineFault::Discordance:   state_ = State::FaultDiscordance;   break;
            }
        } else if (!grip) {
            state_ = State::FaultEnableContacts;
        }
    }

    const bool channelsClosed = channels.value_or(false);
    const bool demand = channelsClosed && enabling_.ready() && !isFault(state_);

    if (!demand) {
        deenergize();
        if (!isFault(state_)) {
            state_ = channelsClosed ? State::StoppedEnable : State::StoppedEstop;
        }
    }

    superviseEdm(dt);

    // Пуск лише по ФРОНТУ кнопки: залипла або перемкнута стяжкою кнопка
    // пуску не має піднімати машину сама.
    const bool resetNow = hal_.readResetButton();
    const bool resetEdge = resetNow && !resetPrev_;
    resetPrev_ = resetNow;

    if (!contactorsOn_ && demand && resetEdge) {
        if (!hal_.readEdmLoop()) {
            // Петля розімкнена при знеструмлених котушках — приварений
            // силовий контакт. Пуск заборонено до обслуговування.
            state_ = State::FaultEdm;
            return;
        }
        hal_.setContactors(true);
        contactorsOn_ = true;
        edmWatch_ = true;
        edmTimer_ = Millis{0};
        state_ = State::Running;
    }
}

}  // namespace safety
