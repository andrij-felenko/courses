/* seibuild.c — зібрати SEI-одиницю з власною телеметрією.
   Збірка: cc -O2 -std=c11 -c seibuild.c                                 */
#include <stdint.h>
#include <string.h>
#include <stddef.h>

/* Згенеровано раз (uuidgen) і заморожено назавжди. */
static const uint8_t TELE_UUID[16] = {
    0x8B,0x5F,0x1E,0x2A, 0x9C,0x44, 0x4D,0x71,
    0xA3,0x0E, 0x2F,0x18,0x77,0xC4,0x91,0x03
};

typedef struct {
    int64_t  t_us;      /* UTC, мікросекунди від епохи      */
    int32_t  lat_e7;    /* градуси × 1e7                    */
    int32_t  lon_e7;
    int32_t  alt_mm;    /* над еліпсоїдом, міліметри        */
    int16_t  yaw_cd;    /* сантиградуси: 18000 = 180.00°    */
    int16_t  pitch_cd;
    int16_t  roll_cd;
    uint16_t seq;       /* лічильник кадрів кодувальника    */
} tele_t;

typedef struct { uint8_t *p; size_t n, cap; } buf_t;

static int put(buf_t *b, uint8_t v)
{
    if (b->n == b->cap) return -1;
    b->p[b->n++] = v;
    return 0;
}

static int put_be(buf_t *b, uint64_t v, int bytes)
{
    for (int i = bytes - 1; i >= 0; i--)
        if (put(b, (uint8_t)(v >> (8 * i))) < 0) return -1;
    return 0;
}

/* payloadType і payloadSize: ланцюжок 0xFF, останній байт < 255 */
static int put_varlen(buf_t *b, size_t v)
{
    while (v >= 255) { if (put(b, 0xFF) < 0) return -1; v -= 255; }
    return put(b, (uint8_t)v);
}

/* Крок 1: RBSP — тіло одиниці без заголовка NAL і без захисних байтів. */
long sei_rbsp(uint8_t *out, size_t cap, const tele_t *t)
{
    buf_t b = { out, 0, cap };
    const size_t payload = 16 + 8 + 4 + 4 + 4 + 2 + 2 + 2 + 2;  /* = 44 */

    if (put_varlen(&b, 5) < 0)       return -1;   /* user_data_unregistered */
    if (put_varlen(&b, payload) < 0) return -1;   /* довжина РОЗПАКОВАНОГО */
    if (b.n + 16 > b.cap)            return -1;
    memcpy(b.p + b.n, TELE_UUID, 16);
    b.n += 16;

    put_be(&b, (uint64_t)t->t_us,     8);
    put_be(&b, (uint32_t)t->lat_e7,   4);
    put_be(&b, (uint32_t)t->lon_e7,   4);
    put_be(&b, (uint32_t)t->alt_mm,   4);
    put_be(&b, (uint16_t)t->yaw_cd,   2);
    put_be(&b, (uint16_t)t->pitch_cd, 2);
    put_be(&b, (uint16_t)t->roll_cd,  2);
    if (put_be(&b, t->seq, 2) < 0)   return -1;

    if (put(&b, 0x80) < 0)           return -1;   /* rbsp_trailing_bits */
    return (long)b.n;
}

/* Крок 2: RBSP → байти потоку. Захист рахується від заголовка NAL. */
long sei_annexb(uint8_t *out, size_t cap, const uint8_t *rbsp, size_t len)
{
    buf_t b = { out, 0, cap };
    int zeros = 0;

    put(&b, 0x00); put(&b, 0x00); put(&b, 0x00); put(&b, 0x01);
    if (put(&b, 0x06) < 0) return -1;             /* nri = 0, тип = 6 */

    for (size_t i = 0; i < len; i++) {
        if (zeros == 2 && rbsp[i] <= 0x03)
            if (put(&b, 0x03) < 0) return -1;      /* захисна трійка */
        if (put(&b, rbsp[i]) < 0) return -1;
        zeros = (rbsp[i] == 0x00) ? zeros + 1 : 0;
    }
    return (long)b.n;
}
