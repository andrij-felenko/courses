uint8_t LinkManager::allocateMavlinkChannel()
{
    for (uint8_t mavlinkChannel = 0; mavlinkChannel < MAVLINK_COMM_NUM_BUFFERS; mavlinkChannel++) {
        if (_mavlinkChannelsUsedBitMask & (1 << mavlinkChannel)) {
            continue;                                   // біт стоїть — номер уже в когось
        }

        mavlink_reset_channel_status(mavlinkChannel);    // прибрати за попереднім орендарем
        mavlink_status_t* const mavlinkStatus = mavlink_get_channel_status(mavlinkChannel);
        mavlinkStatus->flags |= MAVLINK_STATUS_FLAG_OUT_MAVLINK1;

        _mavlinkChannelsUsedBitMask |= (1 << mavlinkChannel);   // і аж тепер — зайняти
        return mavlinkChannel;
    }

    qCWarning(LinkManagerLog) << "allocateMavlinkChannel: all channels reserved!";
    return invalidMavlinkChannel();
}
