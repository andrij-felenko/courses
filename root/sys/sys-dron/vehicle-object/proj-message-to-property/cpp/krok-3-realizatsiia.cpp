// src/Vehicle/FactGroups/VehicleWinchFactGroup.cc
#include "VehicleWinchFactGroup.h"
#include "Vehicle.h"

#include <QtCore/QtMath>
#include <cstdint>

VehicleWinchFactGroup::VehicleWinchFactGroup(QObject *parent)
    : FactGroup(1000, QStringLiteral(":/json/Vehicle/WinchFact.json"), parent)
{
    _addFact(&_lineLengthFact);
    _addFact(&_speedFact);
    _addFact(&_tensionFact);
    _addFact(&_voltageFact);
    _addFact(&_currentFact);
    _addFact(&_motorTempFact);

    // «Даних ще немає» — це не нуль. NaN станція покаже прочерком.
    for (Fact *fact : { &_lineLengthFact, &_speedFact, &_tensionFact,
                        &_voltageFact, &_currentFact, &_motorTempFact }) {
        fact->setRawValue(qQNaN());
    }
}

void VehicleWinchFactGroup::handleMessage(Vehicle *vehicle, const mavlink_message_t &message)
{
    Q_UNUSED(vehicle);

    switch (message.msgid) {
    case MAVLINK_MSG_ID_WINCH_STATUS:
        _handleWinchStatus(message);
        break;
    default:
        break;
    }
}

void VehicleWinchFactGroup::_handleWinchStatus(const mavlink_message_t &message)
{
    mavlink_winch_status_t winch{};
    mavlink_msg_winch_status_decode(&message, &winch);

    // NaN у полі означає «борт не знає» — кладемо його як є, не підміняючи нулем
    lineLength()->setRawValue(winch.line_length);
    speed()->setRawValue(winch.speed);
    tension()->setRawValue(winch.tension);
    voltage()->setRawValue(winch.voltage);
    current()->setRawValue(winch.current);

    // у цілого поля свій знак незнання — переводимо його в той самий NaN
    motorTemp()->setRawValue(winch.temperature == INT16_MAX
                                 ? qQNaN()
                                 : static_cast<double>(winch.temperature));

    const bool moving = (winch.status & MAV_WINCH_STATUS_MOVING) != 0;
    if (moving != _moving) {
        _moving = moving;
        emit movingChanged(_moving);
    }

    _setTelemetryAvailable(true);
}
