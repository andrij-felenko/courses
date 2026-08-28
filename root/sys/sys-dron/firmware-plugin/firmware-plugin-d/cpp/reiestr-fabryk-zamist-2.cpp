FirmwarePlugin *APMFirmwarePluginFactory::firmwarePluginForAutopilot(
        MAV_AUTOPILOT autopilotType, MAV_TYPE vehicleType)
{
    if (autopilotType != MAV_AUTOPILOT_ARDUPILOTMEGA) {
        return nullptr;
    }
    switch (vehicleType) {
    case MAV_TYPE_QUADROTOR:
    case MAV_TYPE_HEXAROTOR:
    case MAV_TYPE_OCTOROTOR:
    case MAV_TYPE_TRICOPTER:
    case MAV_TYPE_COAXIAL:
    case MAV_TYPE_HELICOPTER:
        if (!_arduCopterPluginInstance) {
            _arduCopterPluginInstance = new ArduCopterFirmwarePlugin(this);
        }
        return _arduCopterPluginInstance;
    // …ArduPlane, ArduRover, ArduSub
    default:
        return nullptr;
    }
}
