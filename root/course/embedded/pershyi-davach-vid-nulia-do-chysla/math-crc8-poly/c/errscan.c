#include "errscan.h"
#include "crc8.h"

#define FRAME_BITS 24

/* Один кадр під двома кодами одразу: спотворення накладаємо на обидва
   синхронно, тож порівнюємо коди на однакових помилках. */
typedef struct {
    uint8_t crc[3];
    uint8_t sum[3];
} guarded;

uint8_t checksum8(const uint8_t *data, size_t len)
{
    unsigned acc = 0;
    size_t i;

    if (data == NULL) {
        return 0;
    }
    for (i = 0; i < len; ++i) {
        acc += data[i];
    }
    return (uint8_t)(acc & 0xFFu);
}

static guarded build(uint16_t word)
{
    guarded g;
    const uint8_t data[2] = { (uint8_t)(word >> 8), (uint8_t)word };

    g.crc[0] = data[0];
    g.crc[1] = data[1];
    g.crc[2] = crc8_fast(data, 2);
    g.sum[0] = data[0];
    g.sum[1] = data[1];
    g.sum[2] = checksum8(data, 2);
    return g;
}

static void flip(guarded *g, int bit)
{
    const uint8_t mask = (uint8_t)(0x80u >> (bit % 8));

    g->crc[bit / 8] ^= mask;
    g->sum[bit / 8] ^= mask;
}

static void judge(const guarded *g, errscan_stats *st)
{
    st->checked++;
    if (crc8_fast(g->crc, 2) == g->crc[2]) {
        st->missed_crc++; /* приймач узяв би зіпсований кадр за справжній */
    }
    if (checksum8(g->sum, 2) == g->sum[2]) {
        st->missed_sum++;
    }
}

static void walk(guarded *g, int start, int left, errscan_stats *st)
{
    if (left == 0) {
        judge(g, st);
        return;
    }
    for (int b = start; b <= FRAME_BITS - left; ++b) {
        flip(g, b);
        walk(g, b + 1, left - 1, st);
        flip(g, b); /* повертаємо біт на місце — кадр знову цілий */
    }
}

errscan_stats errscan_flips(uint16_t word, int bits)
{
    errscan_stats st = { 0, 0, 0 };
    guarded g;

    if (bits < 1 || bits > FRAME_BITS) {
        return st; /* нема чого перебирати */
    }
    g = build(word);
    walk(&g, 0, bits, &st);
    return st;
}

/* Інвертує (або повертає назад) біти одного пакетного спотворення. */
static void toggle_burst(guarded *g, int start, int len, unsigned inner)
{
    flip(g, start);
    if (len >= 2) {
        flip(g, start + len - 1);
        for (int k = 0; k < len - 2; ++k) {
            if (inner & (1u << k)) {
                flip(g, start + 1 + k);
            }
        }
    }
}

errscan_stats errscan_bursts(uint16_t word, int max_len)
{
    errscan_stats st = { 0, 0, 0 };
    guarded g;

    if (max_len < 1) {
        return st;
    }
    if (max_len > FRAME_BITS) {
        max_len = FRAME_BITS;
    }
    g = build(word);
    for (int len = 1; len <= max_len; ++len) {
        /* внутрішніх бітів у пакеті len-2, кожен може бути спотворений або ні */
        const unsigned variants = (len >= 2) ? (1u << (len - 2)) : 1u;
        for (int start = 0; start + len <= FRAME_BITS; ++start) {
            for (unsigned inner = 0; inner < variants; ++inner) {
                toggle_burst(&g, start, len, inner);
                judge(&g, &st);
                toggle_burst(&g, start, len, inner);
            }
        }
    }
    return st;
}

void errscan_swap_demo(uint16_t word, uint8_t *sum_ab, uint8_t *sum_ba,
                       uint8_t *crc_ab, uint8_t *crc_ba)
{
    const uint8_t ab[2] = { (uint8_t)(word >> 8), (uint8_t)word };
    const uint8_t ba[2] = { ab[1], ab[0] };

    if (sum_ab != NULL) {
        *sum_ab = checksum8(ab, 2);
    }
    if (sum_ba != NULL) {
        *sum_ba = checksum8(ba, 2);
    }
    if (crc_ab != NULL) {
        *crc_ab = crc8_fast(ab, 2);
    }
    if (crc_ba != NULL) {
        *crc_ba = crc8_fast(ba, 2);
    }
}
