#include <stdint.h>
#include <stddef.h>

#define IPPROTO_TCP  6
#define IPPROTO_UDP 17

/* Долити шматок у біжучу суму; повертає НЕзгорнутий акумулятор,
   щоб шматки можна було ланцюжити. Нулем доповнює хвіст — тож
   непарним може бути ЛИШЕ останній шматок. */
static uint32_t sum_words(const uint8_t *p, size_t len, uint32_t sum)
{
    while (len > 1) {
        sum += (uint32_t)((p[0] << 8) | p[1]);   /* слово в мережевому порядку */
        p   += 2;
        len -= 2;
    }
    if (len)                                     /* непарний хвіст:            */
        sum += (uint32_t)(p[0] << 8);            /* нуль СПРАВА, байт — старший */
    return sum;
}

/* Загорнути перенос. Двох згортань досить для будь-якого uint32_t. */
static uint16_t fold(uint32_t sum)
{
    sum = (sum & 0xFFFF) + (sum >> 16);
    sum = (sum & 0xFFFF) + (sum >> 16);
    return (uint16_t)sum;
}
