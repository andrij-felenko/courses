// Один прохід кадру через увесь ланцюг.
// true  — ділянкова перевірка підняла тривогу, кадр піде наново;
// false — кадр прийнято (можливо, зіпсованим).
bool carry(Bench& b, const uint8_t* src, size_t n, uint8_t* dst) {
    b.dirty = 0;

    Frame f{};                                   // ── відправник
    std::memcpy(f.data, src, n);
    f.len = uint32_t(n);
    f.sum = checksum16(f.data, n);               // сума народжується ТУТ

    b.corrupt(b.wireA, f.data, n);               // ── дріт A → R

    if (checksum16(f.data, f.len) != f.sum) {    // ── ретранслятор: перевірка ділянки
        b.caught_hop += b.dirty;
        return true;
    }
    Frame g{};
    std::memcpy(g.data, f.data, f.len);          // копіювання всередині ретранслятора
    b.corrupt(b.relay, g.data, f.len);           // ← псування МІЖ перевіркою й сумою
    g.len = f.len;
    g.sum = checksum16(g.data, g.len);           // сума рахується З ТОГО, ЩО ВИЙШЛО

    b.corrupt(b.wireB, g.data, g.len);           // ── дріт R → B

    if (checksum16(g.data, g.len) != g.sum) {    // ── отримувач: перевірка ділянки
        b.caught_hop += b.dirty;
        return true;
    }
    std::memcpy(dst, g.data, g.len);
    b.missed_hop += b.dirty;                     // кадр прийнято — і, можливо, дарма
    return false;
}
