// custom/src/FuelCellFactGroup.cc
#include "FuelCellFactGroup.h"

FuelCellFactGroup::FuelCellFactGroup(QObject *parent)
    : FactGroup(1000, QStringLiteral(":/custom/json/FuelCellFact.json"), parent)
{
    _addFact(&_pressureFact);
    _addFact(&_temperatureFact);
    _addFact(&_powerFact);
    _addFact(&_remainingFact);
    _addFact(&_stateFact);
    _addFact(&_faultsFact);

    // Доки модуль не озвався, показувати нема чого — і це не нуль.
    _pressureFact.setRawValue(qQNaN());
    _temperatureFact.setRawValue(qQNaN());
    _powerFact.setRawValue(qQNaN());
    _remainingFact.setRawValue(qQNaN());
}

void FuelCellFactGroup::handleMessage(Vehicle *vehicle, const mavlink_message_t &message)
{
    Q_UNUSED(vehicle)

    if (message.msgid != MAVLINK_MSG_ID_FUELCELL_STATUS) {
        return;
    }

    mavlink_fuelcell_status_t fuelCell{};
    mavlink_msg_fuelcell_status_decode(&message, &fuelCell);

    _pressureFact.setRawValue(
        (fuelCell.pressure == UINT16_MAX) ? qQNaN() : (fuelCell.pressure / 100.0));
    _temperatureFact.setRawValue(
        (fuelCell.temperature == INT16_MAX) ? qQNaN() : (fuelCell.temperature / 100.0));
    _powerFact.setRawValue(fuelCell.power / 10.0);
    _remainingFact.setRawValue(
        (fuelCell.capacity_remaining == UINT8_MAX) ? qQNaN() : fuelCell.capacity_remaining);
    _stateFact.setRawValue(fuelCell.state);
    _faultsFact.setRawValue(fuelCell.faults);

    _setTelemetryAvailable(true);
}
