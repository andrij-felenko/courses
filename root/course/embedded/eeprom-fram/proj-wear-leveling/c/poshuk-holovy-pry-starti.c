// Знайти голову кільця: пройти всі слоти, взяти дійсний із найбільшою послідовністю.
// Викликається ОДИН раз при старті. Якщо всіх зіпсовано (новий чип) — кільце порожнє.
void wl_mount(wl_ring_t *r) {
    r->head_seq  = 0;          // 0 = ще не знайдено жодного дійсного запису
    r->head_slot = 0;

    uint8_t data[WL_DATA_LEN];
    uint32_t seq;
    for (uint16_t i = 0; i < WL_SLOTS; i++) {
        if (wl_read_slot(i, &seq, data) && seq > r->head_seq) {
            r->head_seq  = seq;
            r->head_slot = i;
        }
    }
    // Тепер r->head_slot указує на останній дійсний запис (якщо head_seq > 0);
    // якщо head_seq == 0 — жодного дійсного немає, кільце чисте, пишемо з нуля.
}

// Прочитати поточне значення (останній дійсний запис). Повертає 1, якщо є що читати.
int wl_get(const wl_ring_t *r, uint8_t *data) {
    if (r->head_seq == 0) return 0;            // кільце порожнє — читати нічого
    uint32_t seq;
    return wl_read_slot(r->head_slot, &seq, data);
}
