static int feed(struct conn *c, const uint8_t *p, size_t n) {
    while (n) {
        if (c->need == 0) {                              /* збираємо заголовок */
            size_t take = HDR - c->hdr_n;
            if (take > n) take = n;
            memcpy(c->hdr + c->hdr_n, p, take);
            c->hdr_n += take; p += take; n -= take;
            if (c->hdr_n < HDR) return 0;                /* заголовок ще неповний */
            uint32_t len = (uint32_t)c->hdr[0] << 24 | (uint32_t)c->hdr[1] << 16
                         | (uint32_t)c->hdr[2] <<  8 | (uint32_t)c->hdr[3];
            if (len == 0 || len > MAXBODY) return -1;    /* перевірка ДО виділення пам'яті */
            if (out_append(c, c->hdr, HDR) < 0) return -1;
            c->need = len; c->hdr_n = 0;
        }
        size_t take = c->need < n ? c->need : n;         /* тіло */
        if (out_append(c, p, take) < 0) return -1;
        c->need -= take; p += take; n -= take;
    }
    return 0;
}
