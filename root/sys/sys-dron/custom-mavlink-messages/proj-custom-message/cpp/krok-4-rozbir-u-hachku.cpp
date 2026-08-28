// custom/src/CustomPlugin.cc
bool CustomPlugin::mavlinkMessage(Vehicle *vehicle, LinkInterface *link,
                                  const mavlink_message_t &message)
{
    if (message.msgid == MAVLINK_MSG_ID_PERIMETER_BEACON_STATUS) {
        mavlink_perimeter_beacon_status_t status{};
        mavlink_msg_perimeter_beacon_status_decode(&message, &status);
        _beacon.update(status);
    }
    return QGCCorePlugin::mavlinkMessage(vehicle, link, message);
}
