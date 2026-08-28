#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ORB_WORDS 8                  // 256 бітів = 8 × 32

// один ORB-дескриптор: 256 бітів як 8 слів по 32 біти
typedef struct {
    uint32_t w[ORB_WORDS];
} orb_desc_t;

// набір дескрипторів одного кадру (просто масив + лічильник)
typedef struct {
    const orb_desc_t *d;             // масив дескрипторів
    int count;                       // скільки їх
} orb_set_t;

// результат зіставлення однієї точки
typedef struct {
    int query;                       // індекс у наборі A
    int train;                       // індекс у наборі B (-1 = немає пари)
    int dist;                        // відстань Гаммінга до пари (0..256)
} orb_match_t;
