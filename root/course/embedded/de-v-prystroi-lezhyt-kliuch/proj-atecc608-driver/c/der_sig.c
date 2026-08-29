#include "der_sig.h"

/* Чип віддає R і S як 32 байти з ведучими нулями, а DER вимагає цілого зі
 * знаком у мінімальній формі: нулі спереду зрізаємо, але якщо старший біт
 * лишився одиницею — дописуємо нульовий байт, інакше число стане від'ємним. */
static size_t encode_integer(const uint8_t *value, size_t len, uint8_t *out)
{
    size_t start = 0;
    while (start + 1 < len && value[start] == 0x00u) {
        start++;
    }

    size_t body = len - start;
    int pad = (value[start] & 0x80u) ? 1 : 0;

    size_t i = 0;
    out[i++] = 0x02u;                       /* тег INTEGER */
    out[i++] = (uint8_t)(body + (size_t)pad); /* довжина (завжди < 128) */
    if (pad) {
        out[i++] = 0x00u;
    }
    for (size_t j = 0; j < body; j++) {
        out[i++] = value[start + j];
    }
    return i;
}

size_t der_encode_signature(const uint8_t raw[64], uint8_t *out, size_t cap)
{
    uint8_t body[DER_SIG_MAX];
    size_t len = 0;

    len += encode_integer(&raw[0], 32, &body[len]);   /* R */
    len += encode_integer(&raw[32], 32, &body[len]);  /* S */

    if (cap < len + 2u) {
        return 0;
    }

    out[0] = 0x30u;             /* тег SEQUENCE */
    out[1] = (uint8_t)len;      /* тіло ніколи не сягає 128 байтів */
    for (size_t i = 0; i < len; i++) {
        out[2 + i] = body[i];
    }
    return len + 2u;
}
