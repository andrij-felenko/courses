// Декодування рівня CC із гістерезисом. Пороги в мВ; між UP і DN — мертва смуга.
typedef enum { CC_NONE, CC_DEFAULT, CC_1A5, CC_3A0 } cc_level_t;

// Межі рівнів (середини смуг) і рознесені від них пороги вгору/вниз.
static const int THR_UP[] = { 250, 720, 1300 };  // піднятись на наступний рівень
static const int THR_DN[] = { 150, 600, 1160 };  // зійти на попередній рівень

cc_level_t cc_decode(int mv, cc_level_t cur) {
    // Піднімаємось, лише якщо впевнено вище верхнього порога наступного рівня.
    if (cur < CC_3A0    && mv > THR_UP[cur])     return (cc_level_t)(cur + 1);
    // Сходимо, лише якщо впевнено нижче нижнього порога поточного рівня.
    if (cur > CC_NONE   && mv < THR_DN[cur - 1]) return (cc_level_t)(cur - 1);
    return cur;  // у мертвій смузі — лишаємось як були
}
