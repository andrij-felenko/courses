// Ретранслятор: приймає кадр, перевіряє суму, копіює далі, ставить НОВУ суму.
bool relay(const Frame& in, Frame& out) {
    if (checksum(in.data, in.len) != in.sum)   // ділянка «A → шлюз» чиста?
        return false;                          // тут помилку справді видно

    std::memcpy(out.data, in.data, in.len);    // ← а ось тут ламається байт
    out.len = in.len;
    out.sum = checksum(out.data, out.len);     // сума рахується З ТОГО, ЩО ВИЙШЛО
    return true;                               // ділянка «шлюз → B» теж буде «чиста»
}
