#include <stdint.h>
#include <string.h>
#include <limits.h>

#define REC_WIRE_SIZE 15          /* 1 + 4 + 8 + 2 — рахуємо ми, не компілятор */

struct rec {                      /* у пам'яті — як зручно платформі */
    uint8_t  kind;
    uint32_t id;
    int64_t  ts;
    uint16_t len;
};

/* ── запис у формат ─────────────────────────────────────────────── */
static void put_u16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v >> 8);
    p[1] = (uint8_t)v;
}
static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v >> 24); p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >>  8); p[3] = (uint8_t)v;
}
static void put_u64(uint8_t *p, uint64_t v) {
    put_u32(p,     (uint32_t)(v >> 32));
    put_u32(p + 4, (uint32_t)v);
}

void rec_encode(uint8_t buf[REC_WIRE_SIZE], const struct rec *r) {
    buf[0] = r->kind;
    put_u32(buf + 1,  r->id);
    put_u64(buf + 5,  (uint64_t)r->ts);   /* від'ємний час → доповняльний код */
    put_u16(buf + 13, r->len);
}

/* ── читання з формату ──────────────────────────────────────────── */
static uint16_t get_u16(const uint8_t *p) {
    return (uint16_t)(((uint32_t)p[0] << 8) | p[1]);
}
static uint32_t get_u32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
         | ((uint32_t)p[2] <<  8) |  (uint32_t)p[3];
}
static uint64_t get_u64(const uint8_t *p) {
    return ((uint64_t)get_u32(p) << 32) | get_u32(p + 4);
}

void rec_decode(struct rec *r, const uint8_t buf[REC_WIRE_SIZE]) {
    r->kind = buf[0];
    r->id   = get_u32(buf + 1);
    r->ts   = (int64_t)get_u64(buf + 5);
    r->len  = get_u16(buf + 13);
}
