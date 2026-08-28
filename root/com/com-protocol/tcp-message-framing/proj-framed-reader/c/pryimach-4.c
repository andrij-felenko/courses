static fr_status parse_all(struct conn *c)
{
    size_t off  = 0;      /* скільки байтів буфера вже розібрано */
    size_t need = HDR;    /* скільки байтів треба для наступного кроку */

    while (c->have - off >= HDR) {              /* заголовок цілий? */
        uint32_t len = be32(c->buf + off);
        if (len > MAX_FRAME) return FR_PROTO;   /* стеля — ДО будь-якої арифметики */

        need = (size_t)HDR + len;               /* тепер додавання безпечне */
        if (c->have - off < need) break;        /* тіло ще не все — чекаємо */

        if (c->on_frame(c->user, c->buf + off + HDR, len) != 0)
            return FR_PROTO;                    /* обробник відхилив кадр */

        off  += need;
        need  = HDR;
    }

    if (off) {                                  /* хвіст — на початок буфера */
        memmove(c->buf, c->buf + off, c->have - off);
        c->have -= off;
    }
    return reserve(c, need) ? FR_OK : FR_NOMEM;
}
