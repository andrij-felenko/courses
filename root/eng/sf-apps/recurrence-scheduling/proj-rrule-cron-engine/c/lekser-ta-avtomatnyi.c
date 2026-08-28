static const char* parse_uint_fast(const char *p, uint32_t *out) {
    if (*p < '0' || *p > '9') return NULL;
    uint32_t v = 0;
    while (*p >= '0' && *p <= '9') {
        v = v * 10 + (uint32_t)(*p - '0');
        p++;
    }
    *out = v;
    return p;
}
