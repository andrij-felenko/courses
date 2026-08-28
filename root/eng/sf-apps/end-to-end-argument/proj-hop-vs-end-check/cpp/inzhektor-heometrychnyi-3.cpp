const double   rate = 1e-6;                       // псувань на байт на КОЖНІЙ ділянці
const uint64_t size = 64ull << 20;                // 64 МіБ потоку

Bench b(20260802, rate);
std::mt19937_64 source(1);                        // «файл», який передаємо
std::vector<uint8_t> in(PAYLOAD), out(PAYLOAD);
Fnv1a tx, rx;

while (b.bytes < size) {
    for (size_t i = 0; i < PAYLOAD; ++i) in[i] = uint8_t(source());
    tx.feed(in.data(), PAYLOAD);                  // кінець A — від того, що читає
    while (carry(b, in.data(), PAYLOAD, out.data())) ++b.resent;
    rx.feed(out.data(), PAYLOAD);                 // кінець B — від того, що дійшло
    b.bytes += PAYLOAD;
}
std::printf("зловила ділянка %llu, пройшло далі %llu, геші %s\n",
            (unsigned long long)b.caught_hop, (unsigned long long)b.missed_hop,
            tx.h == rx.h ? "збіглися" : "РОЗІЙШЛИСЯ");
