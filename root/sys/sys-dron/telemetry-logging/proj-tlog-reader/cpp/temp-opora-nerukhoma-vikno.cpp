void playback(TlogReader& log, double speed) {
    using Clock = std::chrono::steady_clock;   // МОНОТОННИЙ: тут ми міряємо
                                               // проміжок, а не позначаємо подію
    uint64_t anchorLogUsec = 0;
    if (!log.pending(anchorLogUsec)) return;
    const Clock::time_point anchorTick = Clock::now();

    std::vector<uint8_t> frame;
    uint64_t t = 0;
    while (log.pending(t)) {
        // ЗНАКОВО. Мітка, менша за опору, у беззнаковій арифметиці дала б
        // 2⁶⁴ мінус дрібниця — і програвач заснув би на 585 тисяч років.
        const int64_t aheadUsec = static_cast<int64_t>(t) - static_cast<int64_t>(anchorLogUsec);
        const int64_t dueMs     = static_cast<int64_t>(aheadUsec / 1000.0 / speed);
        const auto    due       = anchorTick + std::chrono::milliseconds(dueMs);
        const int64_t waitMs    =
            std::chrono::duration_cast<std::chrono::milliseconds>(due - Clock::now()).count();

        if (waitMs >= kBatchWindowMs) {
            std::this_thread::sleep_for(std::chrono::milliseconds(waitMs));
            continue;
        }
        if (!log.next(t, frame)) break;
        emit(t, frame);
    }
}
