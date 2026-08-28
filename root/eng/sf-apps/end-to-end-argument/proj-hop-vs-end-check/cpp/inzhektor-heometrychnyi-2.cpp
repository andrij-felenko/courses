struct Bench {
    Injector wireA, relay, wireB;        // три незалежні джерела псування
    std::mt19937_64 pick;                // вибір другого байта в парі
    std::vector<size_t> hits;

    uint64_t bytes = 0;                  // корисних байтів доставлено
    uint64_t caught_hop = 0, missed_hop = 0, resent = 0;
    size_t   dirty = 0;                  // реальних псувань у поточному кадрі

    Bench(uint64_t seed, double rate)
        : wireA(seed + 1, rate), relay(seed + 2, rate),
          wireB(seed + 3, rate), pick(seed + 4) {}

    void corrupt(Injector& src, uint8_t* d, size_t len) {
        src.advance(len, hits);
        std::uniform_int_distribution<size_t> pos(0, len - 1);
        for (size_t i : hits) {
            size_t j = pos(pick);
            while (j == i) j = pos(pick);
            if (d[i] == d[j]) continue;   // байти однакові — зміни не сталося
            std::swap(d[i], d[j]);
            ++dirty;
        }
    }
};
