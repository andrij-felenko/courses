// Просунути список на bytes переданих байтів.
// ІНВАРІАНТ:  total(до) == bytes + total(після).
// false ⇒ bytes > total; список НЕ змінено. O(зʼїдених сегментів).
bool sg_advance(struct sg_list *sg, size_t bytes) {
    int    i    = 0;
    size_t rest = bytes;

    while (i < sg->n && rest >= sg->seg[i].len) {   // цілі сегменти — геть
        rest -= sg->seg[i].len;
        i++;
    }
    if (i == sg->n && rest > 0) return false;       // просять більше, ніж є

    if (rest > 0) {                                 // влучений — розрізати
        sg->seg[i].addr += rest;                    // база вперед
        sg->seg[i].len  -= rest;                    // довжина менша
    }
    sg->seg += i;                                   // вид зсувається — без memmove
    sg->n   -= i;
    return true;
}
