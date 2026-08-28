// cc_reader.c
#include "cc_reader.h"

#define CC_AVG_N     8     // глибина усереднення (степінь двійки — ділення зсувом)
#define CC_STABLE_N  5     // скільки однакових рівнів поспіль = «сталий»
#define CC_PRESENT_MV 200  // вище цього на лінії — щось під'єднано (не висить)

// ── Кільцевий буфер: один новий відлік за виклик, миттєве середнє ───────────
typedef struct {
    uint16_t buf[CC_AVG_N];
    uint32_t sum;          // біжуча сума вмісту buf
    uint8_t  head;         // куди класти наступний
    uint8_t  count;        // скільки вже накопичено (для «теплого» старту)
} ring_t;

static void ring_reset(ring_t *r) {
    r->sum = 0; r->head = 0; r->count = 0;
    for (uint8_t i = 0; i < CC_AVG_N; i++) r->buf[i] = 0;
}

static uint16_t ring_push(ring_t *r, uint16_t mv) {
    r->sum -= r->buf[r->head];      // викидаємо найстаріший
    r->buf[r->head] = mv;           // кладемо новий на його місце
    r->sum += mv;
    r->head = (r->head + 1) % CC_AVG_N;
    if (r->count < CC_AVG_N) r->count++;
    return (uint16_t)(r->sum / (r->count ? r->count : 1));  // середнє по наявному
}
