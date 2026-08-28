void Vehicle::_handleGlobalPositionInt(mavlink_message_t& message)
{
    if (message.compid != _defaultComponentId) {
        return;
    }
    mavlink_global_position_int_t globalPositionInt;
    mavlink_msg_global_position_int_decode(&message, &globalPositionInt);

    if (!_altitudeMessageAvailable) {                 // якщо є ALTITUDE — беремо звідти
        _altitudeRelativeFact.setRawValue(globalPositionInt.relative_alt / 1000.0);
        _altitudeAMSLFact.setRawValue(globalPositionInt.alt / 1000.0);
    }

    // ArduPilot шле кадри з нулями в широті й довготі навіть без сигналу GPS,
    // щоб доправити самою лише відносну висоту
    if (globalPositionInt.lat == 0 && globalPositionInt.lon == 0) {
        return;
    }

    QGeoCoordinate newPosition(globalPositionInt.lat / 1E7,
                               globalPositionInt.lon / 1E7,
                               globalPositionInt.alt / 1000.0);
    if (newPosition != _coordinate) {
        _coordinate = newPosition;
        emit coordinateChanged(_coordinate);
    }
}
