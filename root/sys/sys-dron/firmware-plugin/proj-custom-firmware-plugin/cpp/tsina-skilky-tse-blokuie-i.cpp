void SokilFirmwarePlugin::adjustOutgoingMavlinkMessageThreadSafe(Vehicle *vehicle,
                                                                 LinkInterface *outgoingLink,
                                                                 mavlink_message_t *message)
{
    if (message->msgid != MAVLINK_MSG_ID_COMMAND_LONG) {
        return;
    }

    mavlink_command_long_t cmd{};
    mavlink_msg_command_long_decode(message, &cmd);
    if (cmd.target_component == MAV_COMP_ID_ALL) {
        cmd.target_component = MAV_COMP_ID_AUTOPILOT1;
        mavlink_msg_command_long_encode_chan(message->sysid, message->compid,
                                             outgoingLink->mavlinkChannel(), message, &cmd);
    }
}
