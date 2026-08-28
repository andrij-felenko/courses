#include <stdint.h>
#include <stddef.h>

// 1. Наївно: гілка на кожній вибірці (страждає на шумі коло порога)
void clip_branch(uint16_t *buf, size_t n, uint16_t thr) {
    for (size_t i = 0; i < n; i++)
        if (buf[i] > thr)
            buf[i] = thr;
}

// 2. Безгілково, маска вручну — видно весь механізм
void clip_mask(uint16_t *buf, size_t n, uint16_t thr) {
    for (size_t i = 0; i < n; i++) {
        uint16_t v    = buf[i];
        uint16_t over = -(uint16_t)(v > thr);   // v>thr → 0xFFFF, інакше 0x0000
        // над порогом беремо thr, під порогом лишаємо v:
        buf[i] = (thr & over) | (v & ~over);
    }
}

// 3. Безгілково й читабельно — те саме через min без гілки
static inline uint16_t umin(uint16_t a, uint16_t b) {
    // b < a ? b : a, але без стрибка:
    uint16_t m = -(uint16_t)(b < a);            // b<a → 0xFFFF
    return (b & m) | (a & ~m);
}
void clip_min(uint16_t *buf, size_t n, uint16_t thr) {
    for (size_t i = 0; i < n; i++)
        buf[i] = umin(buf[i], thr);
}
