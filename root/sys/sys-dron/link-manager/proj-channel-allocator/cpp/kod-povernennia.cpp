void LinkInterface::_freeMavlinkChannel()
{
    if (!mavlinkChannelIsSet()) {
        return;                                    // нема чого повертати
    }

    _signingController.reset();                    // обʼєкт із ключем помирає...

    mavlink_status_t* const status = mavlink_get_channel_status(_mavlinkChannel);
    status->signing = nullptr;                     // ...тож вказівники на нього
    status->signing_streams = nullptr;             //    мусять зникнути тут-таки
    mavlink_reset_channel_status(_mavlinkChannel);

    LinkManager::instance()->freeMavlinkChannel(_mavlinkChannel);
    _mavlinkChannel = LinkManager::invalidMavlinkChannel();   // і забути свій номер
}
