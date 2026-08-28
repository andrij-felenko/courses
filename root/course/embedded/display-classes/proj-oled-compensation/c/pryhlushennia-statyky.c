// один статичний регіон, який інтерфейс сам про себе оголошує
typedef struct {
    uint16_t x, y, w, h;     // де він на екрані
    uint32_t last_change_ms; // коли його востаннє перемалювали
    uint8_t  dim_pct;        // наскільки зараз притлумлено (0 = повна яскравість)
} static_region_t;

// викликається малювальним кодом щоразу, коли елемент реально змінив вміст
void region_touched(static_region_t *r, uint32_t now_ms) {
    r->last_change_ms = now_ms;
    r->dim_pct = 0;          // змінився → знову світить на повну
}

// раз на ~секунду: чим довше регіон не мінявся, тим сильніше тлумимо (до стелі)
void region_age(static_region_t *r, uint32_t now_ms) {
    uint32_t still = now_ms - r->last_change_ms;
    uint8_t  want;
    if      (still <  30000u) want = 0;    // < 30 c — не чіпаємо
    else if (still < 120000u) want = 12;   // 0.5..2 хв — легкий мінус 12 %
    else                      want = 25;   // > 2 хв статики — стеля −25 %
    // повземо до цілі по 1 %/крок, щоб притемнення було непомітним
    if      (r->dim_pct < want) r->dim_pct++;
    else if (r->dim_pct > want) r->dim_pct--;
}
