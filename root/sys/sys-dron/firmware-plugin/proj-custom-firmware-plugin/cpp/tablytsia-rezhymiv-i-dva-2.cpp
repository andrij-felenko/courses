QString SokilFirmwarePlugin::flightMode(uint8_t base_mode, uint32_t custom_mode) const
{
    // Причину переходу в імені режиму не показуємо — вона їде окремим індикатором.
    return FirmwarePlugin::flightMode(base_mode, custom_mode & 0xFF);
}

bool SokilFirmwarePlugin::setFlightMode(const QString &flightMode,
                                        uint8_t *base_mode, uint32_t *custom_mode) const
{
    for (const FirmwareFlightMode &mode : _flightModeList) {
        if (mode.mode_name != flightMode) {
            continue;
        }
        if (!mode.canBeSet) {
            qCWarning(SokilLog) << "режим не можна вибрати вручну:" << flightMode;
            return false;
        }
        *base_mode   = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED;
        *custom_mode = mode.custom_mode;   // причина нульова: перехід ініціює пілот
        return true;
    }

    qCWarning(SokilLog) << "невідомий режим:" << flightMode;
    return false;
}

QStringList SokilFirmwarePlugin::flightModes(Vehicle *vehicle) const
{
    QStringList list;
    for (const FirmwareFlightMode &mode : _flightModeList) {
        if (!mode.canBeSet) {
            continue;
        }
        if ((vehicle->multiRotor() && !mode.multiRotor) || (vehicle->fixedWing() && !mode.fixedWing)) {
            continue;
        }
        list << mode.mode_name;
    }
    return list;
}
