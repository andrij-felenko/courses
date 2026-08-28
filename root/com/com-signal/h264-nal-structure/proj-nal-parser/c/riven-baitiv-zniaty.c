/* Знімає захисні байти 0x03. Пише не більше cap байтів у dst, повертає,
   скільки вийшло. dst може дорівнювати src: записувач ніколи не випереджає
   читача, тому робота йде просто в буфері, без зайвої копії. */
static long unescape(uint8_t *dst, long cap, const uint8_t *src, long len)
{
    long w = 0, zeros = 0;
    for (long r = 0; r < len && w < cap; r++) {
        uint8_t c = src[r];
        if (zeros >= 2 && c == 0x03) { zeros = 0; continue; }
        dst[w++] = c;
        zeros = (c == 0x00) ? zeros + 1 : 0;
    }
    return w;
}
