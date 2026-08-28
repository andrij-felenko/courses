#include <stdint.h>
#include <stdbool.h>

// Ковзне усереднення на кільцевому буфері.
// WIN мусить бути степенем двійки, щоб маска WIN-1 замінила ділення з остачею.
#define WIN        16                 // розмір вікна (степінь 2!)
#define WIN_MASK   (WIN - 1)          // 0b1111 = 15 — для зсуву голови по колу
#define WIN_SHIFT  4                  // log2(WIN): ділення суми на WIN = зсув на 4

typedef struct {
    uint16_t buf[WIN];    // кільце останніх WIN відліків
    uint32_t sum;         // біжуча сума вмісту кільця — 32-бітна (пастка нижче)
    uint16_t head;        // куди пишемо наступний; там же лежить найстаріший
    uint16_t filled;      // скільки комірок уже реально заповнено (для розігріву)
} sliding_t;

// Ініціалізація: усе в нуль.
void sliding_init(sliding_t *s) {
    for (uint16_t i = 0; i < WIN; i++) s->buf[i] = 0;
    s->sum = 0;
    s->head = 0;
    s->filled = 0;
}

// Згодувати новий відлік, отримати згладжене середнє вікна.
uint16_t sliding_push(sliding_t *s, uint16_t sample) {
    s->sum -= s->buf[s->head];        // прибрати найстаріший (він саме під головою)
    s->sum += sample;                 // додати новий
    s->buf[s->head] = sample;         // перезаписати комірку
    s->head = (s->head + 1) & WIN_MASK; // зсунути голову по колу (дешева маска)

    if (s->filled < WIN) s->filled++; // поки вікно набирається — рахуємо реальний вміст

    return (uint16_t)(s->sum / s->filled); // середнє по вже заповненій частині
}
