uint16_t calculate_keytag(const uint8_t *rdata, size_t rdata_len, uint8_t algorithm) {
    if (algorithm == 1) { /* RSAMD5 крайовий випадок */
        if (rdata_len < 3) return 0;
        return (uint16_t)((rdata[rdata_len - 3] << 8) | rdata[rdata_len - 2]);
    }

    uint32_t ac = 0;
    for (size_t i = 0; i < rdata_len; ++i) {
        ac += (i & 1) ? rdata[i] : (rdata[i] << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return (uint16_t)(ac & 0xFFFF);
}
