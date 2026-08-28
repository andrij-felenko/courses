#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint8_t *buf;        /* вихідний буфер           */
    size_t   cap, len;   /* місткість і заповнення    */
    uint32_t acc;        /* накопичувач біт           */
    int      nbits;      /* скільки біт в acc (0..31) */
} bitw_t;

static void bw_init(bitw_t *w, uint8_t *buf, size_t cap) {
    w->buf = buf; w->cap = cap; w->len = 0; w->acc = 0; w->nbits = 0;
}

static void bw_put(bitw_t *w, uint32_t bits, int n) {  /* записати n молодших біт */
    w->acc |= (bits & ((n == 32) ? 0xFFFFFFFFu : ((1u << n) - 1))) << (32 - n - w->nbits);
    w->nbits += n;
    while (w->nbits >= 8) {
        if (w->len < w->cap) w->buf[w->len++] = (uint8_t)(w->acc >> 24);
        w->acc <<= 8;
        w->nbits -= 8;
    }
}

static void bw_flush(bitw_t *w) {                      /* доповнити останній байт */
    if (w->nbits > 0 && w->len < w->cap) {
        w->buf[w->len++] = (uint8_t)(w->acc >> 24);
        w->acc = 0; w->nbits = 0;
    }
}
