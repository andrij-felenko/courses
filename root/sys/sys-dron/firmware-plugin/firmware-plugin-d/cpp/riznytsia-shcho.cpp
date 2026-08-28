QString APMFirmwarePlugin::missionCommandOverrides(QGCMAVLink::VehicleClass_t vehicleClass) const
{
    switch (vehicleClass) {
    case QGCMAVLink::VehicleClassGeneric:    return QStringLiteral(":/json/APM-MavCmdInfoCommon.json");
    case QGCMAVLink::VehicleClassMultiRotor: return QStringLiteral(":/json/APM-MavCmdInfoMultiRotor.json");
    case QGCMAVLink::VehicleClassFixedWing:  return QStringLiteral(":/json/APM-MavCmdInfoFixedWing.json");
    case QGCMAVLink::VehicleClassVTOL:       return QStringLiteral(":/json/APM-MavCmdInfoVTOL.json");
    case QGCMAVLink::VehicleClassSub:        return QStringLiteral(":/json/APM-MavCmdInfoSub.json");
    case QGCMAVLink::VehicleClassRoverBoat:  return QStringLiteral(":/json/APM-MavCmdInfoRover.json");
    }
}
