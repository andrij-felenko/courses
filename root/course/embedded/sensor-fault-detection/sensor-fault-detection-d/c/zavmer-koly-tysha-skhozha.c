typedef struct {
    float    eps;            // поріг: менший рух вважаємо «нерухомістю»
    uint16_t limit;          // скільки нерухомих відліків — це вже завмер
    float    ref;            // опорне значення, від якого міряємо рух
    uint16_t still;          // лічильник нерухомих відліків поспіль
} stuck_det_t;

bool is_stuck(stuck_det_t *s, float x) {
    if (fabsf(x - s->ref) < s->eps) {     // рух менший за власний шум давача
        if (s->still < 0xFFFF) s->still++;
    } else {
        s->ref = x;                       // ворухнулося — оновлюємо опору
        s->still = 0;
    }
    return s->still >= s->limit;          // надто довго мертво нерухоме
}
