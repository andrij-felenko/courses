// buf — накопичувач з'єднання, have — скільки в ньому байтів
static int on_readable(struct conn *c) {
    ssize_t n = recv(c->fd, c->buf + c->have, sizeof c->buf - c->have, 0);
    if (n < 0) return (errno == EAGAIN) ? OK : ERR_IO;
    if (n == 0) return (c->have == 0) ? CLEAN_EOF : ERR_TRUNCATED;
    c->have += (size_t)n;

    size_t off = 0;                          // скільки з буфера вже розібрано
    while (c->have - off >= HDR) {           // заголовок цілий?
        uint32_t len = be32(c->buf + off);   // довжина зі старшим байтом уперед
        if (len > MAX_FRAME) return ERR_PROTO;    // стеля — ДО будь-якої арифметики
        if (c->have - off < HDR + len) break;     // тіло ще не все — чекаємо далі
        handle_frame(c->buf + off + HDR, len);
        off += HDR + len;
    }
    memmove(c->buf, c->buf + off, c->have - off); // хвіст — на початок буфера
    c->have -= off;
    return OK;
}
