/* Сума заголовка IPv4: поле суми — на зсуві 10. */
uint16_t ip_checksum(uint8_t *hdr, size_t hdr_len)
{
    hdr[10] = 0;                                  /* занулити поле суми! */
    hdr[11] = 0;
    uint16_t c = (uint16_t)~fold(sum_words(hdr, hdr_len, 0));
    hdr[10] = (uint8_t)(c >> 8);
    hdr[11] = (uint8_t)(c & 0xFF);
    return c;
}

/* Сума UDP поверх IPv4: поле — на зсуві 6. */
uint16_t udp_checksum_v4(const uint8_t src[4], const uint8_t dst[4],
                         uint8_t *udp, size_t udp_len)
{
    udp[6] = 0;                                   /* занулити поле суми! */
    udp[7] = 0;
    uint32_t sum = pseudo_v4(src, dst, IPPROTO_UDP, (uint16_t)udp_len, 0);
    sum = sum_words(udp, udp_len, sum);           /* заголовок UDP + дані */
    uint16_t c = (uint16_t)~fold(sum);
    if (c == 0x0000)
        c = 0xFFFF;                               /* трюк UDP: нуль шлемо як −0 */
    udp[6] = (uint8_t)(c >> 8);
    udp[7] = (uint8_t)(c & 0xFF);
    return c;
}

/* Сума TCP поверх IPv4: те саме, але поле — на зсуві 16 і БЕЗ трюку з нулем. */
uint16_t tcp_checksum_v4(const uint8_t src[4], const uint8_t dst[4],
                         uint8_t *tcp, size_t tcp_len)
{
    tcp[16] = 0;
    tcp[17] = 0;
    uint32_t sum = pseudo_v4(src, dst, IPPROTO_TCP, (uint16_t)tcp_len, 0);
    sum = sum_words(tcp, tcp_len, sum);
    uint16_t c = (uint16_t)~fold(sum);            /* 0x0000 у TCP — законне значення */
    tcp[16] = (uint8_t)(c >> 8);
    tcp[17] = (uint8_t)(c & 0xFF);
    return c;
}

/* Перевірка на приймачі: сумуємо ВСЕ разом із полем — мусить вийти 0xFFFF. */
int udp_verify_v4(const uint8_t src[4], const uint8_t dst[4],
                  const uint8_t *udp, size_t udp_len)
{
    if (udp[6] == 0 && udp[7] == 0)
        return 1;                                 /* в IPv4 нуль = «суми нема» */
    uint32_t sum = pseudo_v4(src, dst, IPPROTO_UDP, (uint16_t)udp_len, 0);
    sum = sum_words(udp, udp_len, sum);
    return fold(sum) == 0xFFFF;
}
