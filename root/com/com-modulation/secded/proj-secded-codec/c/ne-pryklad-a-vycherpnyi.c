#include <stdio.h>

static const char *NAME[] = {
    "NO_ERROR", "CORRECTED_SINGLE", "PARITY_BIT_ERROR", "DETECTED_DOUBLE"
};

static void show(uint8_t w, char *out)     /* "0110011|0" — позиції 1..7, тоді P₀ */
{
    int i;
    for (i = 0; i < 7; i++) out[i] = (char)('0' + ((w >> i) & 1));
    out[7] = '|';
    out[8] = (char)('0' + ((w >> 7) & 1));
    out[9] = '\0';
}

static void bits4(uint8_t d, char *out)
{
    int i;
    for (i = 0; i < 4; i++) out[i] = (char)('0' + ((d >> (3 - i)) & 1));
    out[4] = '\0';
}

int main(void)
{
    char buf[10], d4[5];
    int d, i, j, k;
    int ok_clean = 0, ok_single = 0, ok_p0 = 0, ok_double = 0;
    int tot3 = 0, silent3 = 0;
    secded_result r;

    uint8_t w = secded_encode(0xB);                  /* дані 1011 */
    show(w, buf);
    printf("дані 1011  ->  слово %s   (позиції 1..7 | P0)\n", buf);

    r = secded_decode(w ^ (1u << 4));                /* збій позиції 5 */
    bits4(r.data, d4);
    printf("  збій поз.5    : синдром=%u -> %-16s поз.%u дані=%s\n",
           (unsigned)r.syndrome, NAME[r.status], (unsigned)r.position, d4);

    r = secded_decode(w ^ (1u << 4) ^ (1u << 5));    /* збій позицій 5 і 6 */
    printf("  збій поз.5+6  : синдром=%u -> %-16s дані НЕ віддано\n",
           (unsigned)r.syndrome, NAME[r.status]);

    r = secded_decode(w ^ 0x80u);                    /* збій самого P₀ */
    bits4(r.data, d4);
    printf("  збій самого P0: синдром=%u -> %-16s дані=%s\n",
           (unsigned)r.syndrome, NAME[r.status], d4);

    for (d = 0; d < 16; d++) {
        uint8_t cw = secded_encode((uint8_t)d);

        r = secded_decode(cw);
        if (r.status == SECDED_NO_ERROR && r.data == d) ok_clean++;

        for (i = 0; i < 7; i++) {                    /* збій одного біта Геммінга */
            r = secded_decode(cw ^ (uint8_t)(1u << i));
            if (r.status == SECDED_CORRECTED_SINGLE && r.data == d
                && r.position == i + 1) ok_single++;
        }

        r = secded_decode(cw ^ 0x80u);               /* збій самого P₀ */
        if (r.status == SECDED_PARITY_BIT_ERROR && r.data == d) ok_p0++;

        for (i = 0; i < 8; i++)                      /* усі пари */
            for (j = i + 1; j < 8; j++) {
                r = secded_decode(cw ^ (uint8_t)(1u << i) ^ (uint8_t)(1u << j));
                if (r.status == SECDED_DETECTED_DOUBLE) ok_double++;
            }

        for (i = 0; i < 8; i++)                      /* усі трійки — межа коду */
            for (j = i + 1; j < 8; j++)
                for (k = j + 1; k < 8; k++) {
                    r = secded_decode(cw ^ (uint8_t)(1u << i)
                                         ^ (uint8_t)(1u << j)
                                         ^ (uint8_t)(1u << k));
                    tot3++;
                    if (r.status != SECDED_DETECTED_DOUBLE && r.data != d) silent3++;
                }
    }

    printf("\nвичерпний перебір усіх 16 слів:\n");
    printf("  чистих слів     :  %3d/%3d  NO_ERROR\n", ok_clean, 16);
    printf("  одиничних збоїв :  %3d/%3d  CORRECTED_SINGLE, дані відновлено\n", ok_single, 112);
    printf("  збоїв P0        :  %3d/%3d  PARITY_BIT_ERROR, дані цілі\n", ok_p0, 16);
    printf("  подвійних збоїв :  %3d/%3d  DETECTED_DOUBLE, жоден не проліз\n", ok_double, 448);
    printf("  потрійних збоїв :  %3d/%3d  тихо зіпсовано — це МЕЖА, а не діра\n", silent3, tot3);
    return 0;
}
