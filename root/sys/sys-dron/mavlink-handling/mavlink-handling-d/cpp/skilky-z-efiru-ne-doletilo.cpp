uint8_t& lastSeq = _lastIndex[mavlinkChannel][message.sysid][message.compid];

const QPair<uint8_t, uint8_t> key(message.sysid, message.compid);
uint8_t expectedSeq;
if (!_firstMessageSeen[mavlinkChannel].contains(key)) {
    _firstMessageSeen[mavlinkChannel].insert(key);
    expectedSeq = message.seq;
} else if (message.seq == lastSeq) {
    return;
} else {
    expectedSeq = lastSeq + 1;
}

uint64_t lostMessages;
if (message.seq >= expectedSeq) {
    lostMessages = message.seq - expectedSeq;
} else {
    lostMessages = static_cast<uint64_t>(message.seq) + 256ULL - expectedSeq;
}
_totalLossCounter[mavlinkChannel] += lostMessages;
