bool TlogReader::seekToTime(uint64_t tUsec) {
    if (_index.empty()) return false;

    auto it = std::upper_bound(_index.begin(), _index.end(), tUsec,
                               [](uint64_t t, const IndexEntry& e) { return t < e.tUsec; });
    const IndexEntry& e = (it == _index.begin()) ? _index.front() : *(it - 1);
    if (!positionAtRecord(e.offset)) return false;

    std::vector<uint8_t> skip;
    uint64_t t = 0;
    while (_hasPending && _pendingT < tUsec) {
        if (!next(t, skip)) break;
    }
    return true;
}
