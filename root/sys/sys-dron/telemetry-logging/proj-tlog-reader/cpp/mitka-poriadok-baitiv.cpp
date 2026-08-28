struct RawStamp { uint64_t raw; int64_t off; };   // мітка ЯК Є, без тлумачення

bool chooseSwapped(const std::vector<RawStamp>& head) {
    const uint64_t nowUsec  = static_cast<uint64_t>(std::time(nullptr)) * kUsecPerSec;
    const uint64_t ceilUsec = nowUsec + 365ULL * 86400ULL * kUsecPerSec;

    auto score = [&](bool swapped) {
        int      s = 0;
        uint64_t prev = 0;
        bool     havePrev = false;
        for (const RawStamp& h : head) {
            const uint64_t t = swapped ? swap64(h.raw) : h.raw;
            s += (t >= kStampFloorUsec && t <= ceilUsec) ? +1 : -1;
            if (havePrev) s += (t >= prev) ? +1 : -1;
            prev = t;
            havePrev = true;
        }
        return s;
    };

    return score(true) > score(false);   // рівність → старший-перший, як велить формат
}
