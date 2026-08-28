// НЕ РОБІТЬ ТАК: проріджування без фільтра.
// Бере кожен D-тий біт і викидає решту 63/64 інформації.
static int pdm_decimate_broken(const uint8_t *pdm, int nbytes,
                               int D, int16_t *out) {
    int8_t bits[8];
    int phase = 0, nout = 0;
    for (int i = 0; i < nbytes; i++) {
        pdm_unpack_byte(pdm[i], bits);
        for (int k = 0; k < 8; k++) {
            if (++phase < D) continue;
            phase = 0;
            // один-єдиний біт як цілий відлік: ±32767, без усереднення
            out[nout++] = bits[k] > 0 ? 32767 : -32768;
        }
    }
    return nout;
}
