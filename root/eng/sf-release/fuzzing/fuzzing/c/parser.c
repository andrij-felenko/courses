// parser.c — функція під тестом
#include <stdint.h>
#include <string.h>

#define MAX_PAYLOAD 128

int parse_frame(const uint8_t *data, size_t size) {
    if (size < 2) return -1;                 // бракує навіть заголовка

    uint16_t len = (data[0] << 8) | data[1]; // оголошена довжина навантаження

    uint8_t buf[MAX_PAYLOAD];
    // ПАСТКА: len узято з входу й НЕ звірено з MAX_PAYLOAD та з size
    memcpy(buf, data + 2, len);              // переповнення буфера за len > 128
                                             // і читання за межами за len > size-2
    return buf[0];
}
