// Скільки байтів проходить до ПЕРШОГО псування, якого ділянкові
// перевірки не побачили. Кожен прогін — незалежний потік.
uint64_t bytes_to_first_miss(uint64_t seed, double rate) {
    Bench b(seed, rate);
    std::mt19937_64 source(seed ^ 0x9e3779b97f4a7c15ull);
    std::vector<uint8_t> in(PAYLOAD), out(PAYLOAD);
    for (;;) {
        for (size_t i = 0; i < PAYLOAD; ++i) in[i] = uint8_t(source());
        while (carry(b, in.data(), PAYLOAD, out.data())) {}
        b.bytes += PAYLOAD;
        if (b.missed_hop) return b.bytes;
    }
}
