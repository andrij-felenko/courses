#include <stdint.h>
#include <stddef.h>

/* Заголовок за таблицею: magic(2) ver(1) flags(1) len(2) rsv(2) time_us(8). */
size_t enc_header(uint8_t *b, uint16_t len, uint64_t t_us)
{
    b[0] = 0xA7;  b[1] = 0x5E;                 /* magic */
    b[2] = 2;                                  /* ver   */
    b[3] = 0;                                  /* flags */
    b[4] = (uint8_t)(len >> 8);  b[5] = (uint8_t)len;
    b[6] = 0;     b[7] = 0;                    /* rsv, завжди нулі */
    for (int i = 0; i < 8; i++)
        b[8 + i] = (uint8_t)(t_us >> (56 - 8 * i));
    return 16;
}
