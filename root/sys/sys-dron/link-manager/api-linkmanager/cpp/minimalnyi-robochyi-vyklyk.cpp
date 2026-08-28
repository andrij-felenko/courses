void broadcastGcsHeartbeat(uint8_t sysid, uint8_t compid)
{
    // links() віддає КОПІЮ списку; спільні вказівники в ній тримають
    // з'єднання живими доти, доки жива сама копія
    for (const SharedLinkInterfacePtr &link : LinkManager::instance()->links()) {
        if (!link->isConnected() || !link->mavlinkChannelIsSet()) {
            continue;                  // ще не з'єдналося або номера каналу нема
        }

        mavlink_message_t msg;
        mavlink_msg_heartbeat_pack_chan(
            sysid, compid, link->mavlinkChannel(), &msg,
            MAV_TYPE_GCS, MAV_AUTOPILOT_INVALID,
            MAV_MODE_MANUAL_ARMED, 0, MAV_STATE_ACTIVE);

        link->sendMessageThreadSafe(msg);   // єдина точка відправки
    }
}
