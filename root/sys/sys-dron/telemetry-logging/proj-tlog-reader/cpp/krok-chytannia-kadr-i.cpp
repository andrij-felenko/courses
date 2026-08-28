bool TlogReader::next(uint64_t& tUsec, std::vector<uint8_t>& frame) {
    if (!_hasPending) return false;
    tUsec = _pendingT;
    frame.clear();

    // Межа кадру відома точно — він починається одразу після мітки. Тому стан
    // каналу скидаємо на КОЖНОМУ записі; у живому лінку таке скидання з'їдало б
    // недозібраний кадр, а тут воно робить записи незалежними один від одного.
    mavlink_reset_channel_status(kChannel);

    mavlink_message_t msg{};
    mavlink_status_t  st{};
    uint8_t b = 0;
    while (_f.getByte(b)) {
        frame.push_back(b);
        if (mavlink_parse_char(kChannel, b, &msg, &st)) {
            uint8_t stamp[kStampBytes];
            _hasPending = _f.read(stamp, kStampBytes);   // мітка НАСТУПНОГО запису
            if (_hasPending) _pendingT = decode(stamp);
            return true;
        }
        if (frame.size() > MAVLINK_MAX_PACKET_LEN) break;
    }
    _hasPending = false;
    _truncated  = true;
    return false;
}
