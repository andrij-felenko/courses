#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Безпечне завантаження скаляра з буфера з урахуванням вирівнювання */
static inline uint32_t load_u32_le(const uint8_t *src) {
    uint32_t val;
    memcpy(&val, src, sizeof(val));
    return val;
}

/* Структура безпечного доступу до таблиці без копіювання */
typedef struct {
    const uint8_t *buf;
    size_t size;
    const uint8_t *table;
    const uint8_t *vtable;
    uint16_t vtable_len;
} packet_view_t;

bool packet_view_init(packet_view_t *view, const uint8_t *buf, size_t size) {
    if (!view || !buf || size < 8) return false;
    view->buf = buf;
    view->size = size;

    uint32_t root_off = load_u32_le(buf);
    if (root_off >= size || size - root_off < 4) return false;
    view->table = buf + root_off;

    int32_t vtable_soff = (int32_t)load_u32_le(view->table);
    ptrdiff_t vtable_abs = (view->table - buf) - vtable_soff;
    if (vtable_abs < 0 || (size_t)vtable_abs + 4 > size) return false;

    view->vtable = buf + vtable_abs;
    memcpy(&view->vtable_len, view->vtable, 2);
    return true;
}

uint32_t packet_get_price(const packet_view_t *view, uint16_t field_idx, uint32_t def_val) {
    size_t voff_pos = 4 + field_idx * 2;
    if (voff_pos + 2 > view->vtable_len) return def_val;

    uint16_t field_off;
    memcpy(&field_off, view->vtable + voff_pos, 2);
    if (field_off == 0) return def_val;

    return load_u32_le(view->table + field_off);
}
