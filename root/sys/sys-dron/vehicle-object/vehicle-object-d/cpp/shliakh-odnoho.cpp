void Vehicle::_mavlinkMessageReceived(LinkInterface* link, mavlink_message_t message)
{
    if (message.sysid != _systemID && message.sysid != 0) {
        // виняток: RADIO_STATUS шле сам модем, у нього власний sysid,
        // але стосується він каналу, яким користується цей апарат
        if (!(message.msgid == MAVLINK_MSG_ID_RADIO_STATUS
              && _vehicleLinkManager->containsLink(link))) {
            return;
        }
    }
    ...
