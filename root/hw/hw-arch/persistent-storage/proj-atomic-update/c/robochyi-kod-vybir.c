// Прочитати слот і сказати, чи він цілий (CRC зійшовся).
static bool slot_valid(int slot, Record *out) {
    flash_read_slot(slot, out);
    return record_crc(out) == out->crc;
}

// Повернути номер чинного слоту (0/1), або -1 якщо цілого нема
// (перший старт у житті пристрою, або обидва слоти пошкоджені).
int active_slot(void) {
    Record a, b;
    bool ok_a = slot_valid(SLOT_A, &a);
    bool ok_b = slot_valid(SLOT_B, &b);

    if (ok_a && ok_b) {
        // Обидва цілі — беремо новіший за seq.
        return seq_newer(a.seq, b.seq) ? SLOT_A : SLOT_B;
    }
    if (ok_a) return SLOT_A;   // цілий лише A
    if (ok_b) return SLOT_B;   // цілий лише B
    return -1;                 // цілого нема
}

// Прочитати seq чинного слоту (викликати лише коли active_slot() >= 0).
uint32_t read_seq(int slot) {
    Record r;
    flash_read_slot(slot, &r);
    return r.seq;
}
