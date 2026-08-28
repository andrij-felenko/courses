void Vehicle::setFlightMode(const QString &flightMode)
{
    uint8_t base_mode; uint32_t custom_mode;
    if (setFlightModeCustom(flightMode, &base_mode, &custom_mode)) {
        …
        if (_firmwarePlugin->MAV_CMD_DO_SET_MODE_is_supported()) {
            sendMavCommand(defaultComponentId(), MAV_CMD_DO_SET_MODE, true,
                           MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, custom_mode);
        } else {
            // запасна дорога для прошивок без DO_SET_MODE — старе повідомлення SET_MODE
            mavlink_msg_set_mode_pack_chan(…, id(), newBaseMode, custom_mode);
            sendMessageOnLinkThreadSafe(sharedLink.get(), msg);
        }
    }
}
