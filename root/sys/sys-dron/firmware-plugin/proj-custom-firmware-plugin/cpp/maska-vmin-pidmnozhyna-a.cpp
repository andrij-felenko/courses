bool SokilFirmwarePlugin::isCapable(const Vehicle *vehicle, FirmwareCapabilities capabilities) const
{
    int available = SetFlightModeCapability | GuidedModeCapability | PauseVehicleCapability;

    if (vehicle->multiRotor()) {
        available |= TakeoffVehicleCapability | GuidedTakeoffCapability | ChangeHeadingCapability;
    }
    // OrbitModeCapability і ROIModeCapability Sokil не має: підвісу немає,
    // а політ по колу не реалізовано в прошивці.

    return (capabilities & available) == capabilities;
}
