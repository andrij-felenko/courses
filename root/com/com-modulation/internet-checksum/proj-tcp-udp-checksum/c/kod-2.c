/* IPv4: адреси по 4 байти, нульовий байт + протокол = одне слово, довжина. */
static uint32_t pseudo_v4(const uint8_t src[4], const uint8_t dst[4],
                          uint8_t proto, uint16_t seg_len, uint32_t sum)
{
    sum  = sum_words(src, 4, sum);
    sum  = sum_words(dst, 4, sum);
    sum += (uint32_t)proto;        /* слово «нулі|протокол»: 0x0011 для UDP */
    sum += (uint32_t)seg_len;      /* довжина TCP/UDP: заголовок + дані     */
    return sum;
}

/* IPv6: адреси по 16 байтів, 32-бітна довжина, три нулі + Next Header. */
static uint32_t pseudo_v6(const uint8_t src[16], const uint8_t dst[16],
                          uint8_t next_hdr, uint32_t ulp_len, uint32_t sum)
{
    sum  = sum_words(src, 16, sum);
    sum  = sum_words(dst, 16, sum);
    sum += (ulp_len >> 16) & 0xFFFF;   /* довжина тут 32-бітна — двома словами */
    sum += ulp_len & 0xFFFF;
    sum += (uint32_t)next_hdr;         /* три нульові байти + Next Header      */
    return sum;
}
