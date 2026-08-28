#include <stdint.h>    // uintptr_t, SIZE_MAX
#include <stddef.h>    // size_t
#include <string.h>    // memcpy
#include <stdbool.h>

// Один суцільний клапоть. Простір адреси НЕ закодовано в типі —
// його задає той, хто список побудував (див. контракт кожної функції).
struct sg_seg {
    uintptr_t addr;    // початок клаптя
    size_t    len;     // скільки байтів у клапті
};

// ВИД (view) на масив сегментів. НЕ власник памʼяті: під масив хтось
// інший (виклик, арена, пул драйвера) уже виділив місце.
struct sg_list {
    struct sg_seg *seg;   // куди дивимось зараз
    int            n;     // скільки сегментів попереду
};
