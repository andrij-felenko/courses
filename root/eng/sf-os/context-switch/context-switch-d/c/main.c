#include <stdint.h>

// Блок керування задачею: головне тут — куди сховати верхівку стека.
typedef struct {
    uint32_t *saved_sp;   // збережений вказівник стека цієї задачі
} TCB;

TCB *current;             // хто біжить зараз
TCB *next;                // кого пускаємо

// Псевдо-«штовхнути регістр на стек» і «зняти зі стека».
// (На залізі це роблять інструкції push/pop; тут — щоб побачити суть.)
static inline void push(uint32_t **sp, uint32_t v) { *(--(*sp)) = v; }
static inline uint32_t pop(uint32_t **sp)          { return *((*sp)++); }

// Серце перемикання: три знайомі кроки.
void switch_context(uint32_t r0, uint32_t r1, uint32_t pc) {
    uint32_t *sp = current->saved_sp;

    // КРОК 1 — зберегти контекст ПОТОЧНОЇ задачі на ЇЇ стек.
    push(&sp, pc);        // куди повертатись (лічильник команд)
    push(&sp, r1);        // робочі регістри…
    push(&sp, r0);
    current->saved_sp = sp;   // запам'ятати верхівку в TCB поточної

    // КРОК 2 — підмінити SP: ядро «стає» наступною задачею.
    current = next;
    sp = current->saved_sp;   // тепер працюємо зі стеком НАСТУПНОЇ

    // КРОК 3 — відновити контекст НАСТУПНОЇ задачі з ЇЇ стека
    // (у зворотному порядку — стек є LIFO).
    uint32_t nr0 = pop(&sp);
    uint32_t nr1 = pop(&sp);
    uint32_t npc = pop(&sp);
    current->saved_sp = sp;
    // повернення на npc з відновленими nr0, nr1 — і біжить уже наступна задача
    (void)nr0; (void)nr1; (void)npc;
}
