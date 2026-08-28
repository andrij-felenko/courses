// Забрати з купи блок, що сидить на позиції i (не конче в корені).
static uint16_t heap_take(int i) {
    uint16_t b = heap[i];
    hpos[b] = NO_BLOCK;
    heap_n--;
    if (i != heap_n) {                     // дірку затикаємо останнім елементом
        uint16_t last = heap[heap_n];
        heap[i] = last;
        hpos[last] = i;
        sift_down(i);                      // він може виявитися завеликим…
        sift_up(i);                        // …або замалим — тож пробуємо обидва боки
    }
    return b;
}

static uint16_t heap_pop_min(void) {       // найменш зношений вільний блок
    return heap_n ? heap_take(0) : NO_BLOCK;
}
