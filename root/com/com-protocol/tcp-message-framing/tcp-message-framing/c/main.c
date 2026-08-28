c->have += n;                                // n байтів щойно дописано в кінець буфера
size_t off = 0;                              // скільки з буфера вже розібрано
while (c->have - off >= HDR) {               // заголовок цілий?
    uint32_t len = be32(c->buf + off);       // довжина зі старшим байтом уперед
    if (len > MAX_FRAME) return ERR_PROTO;   // стеля — ДО будь-якої арифметики
    if (c->have - off < HDR + len) break;    // тіло ще не все — чекаємо далі
    handle_frame(c->buf + off + HDR, len);
    off += HDR + len;
}
memmove(c->buf, c->buf + off, c->have - off);  // хвіст — на початок буфера
c->have -= off;
