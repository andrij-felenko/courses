uint8_t LinkManager::allocateMavlinkChannel()
{
    for (uint8_t ch = 0; ch < MAVLINK_COMM_NUM_BUFFERS; ch++) {
        if (_mavlinkChannelsUsedBitMask & (1 << ch)) continue;
        mavlink_reset_channel_status(ch);
        mavlink_get_channel_status(ch)->flags |= MAVLINK_STATUS_FLAG_OUT_MAVLINK1;
        _mavlinkChannelsUsedBitMask |= (1 << ch);
        return ch;
    }
    return invalidMavlinkChannel();          // 0xFF
}
