#include <stdint.h>

#define PRIO_SENSOR  2   // давач — високий
#define PRIO_LOG     1   // лог    — низький
#define PRIO_DISPLAY 1   // дисплей — низький

// Біт i = 1 → на пріоритеті i є хоч одна готова задача.
static uint32_t ready_bits = 0;

static inline void mark_ready(int prio)   { ready_bits |=  (1u << prio); }
static inline void mark_blocked(int prio) { ready_bits &= ~(1u << prio); }

// Найвищий готовий пріоритет: позиція найстаршої одиниці слова.
// __builtin_clz рахує старші нулі; 31 − clz і є цей номер.
static int next_priority(void) {
    if (ready_bits == 0) return -1;          // готових немає (на МК так не буває:
    return 31 - __builtin_clz(ready_bits);   // на рівні 0 завжди є задача простою)
}
