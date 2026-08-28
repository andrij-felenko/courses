#include <stdbool.h>

static bool en_prev = false;
static bool q_latch = false;

// латч: цілий рівень — вікно захоплення
void latch_capture(bool data, bool en) {
    if (en) {
        q_latch = data;               // прозоро: тече за входом весь час, доки en=1
    }
    // на спаді en 1→0 останнє значення просто лишається в q_latch — це й є «фіксація»
    en_prev = en;
    // дані, що змінилися пізно, АЛЕ доки en ще =1, встигли пройти — це і є позика часу
}
