// М'яке підрівнювання T₀: беремо більшість зі старого, дрібку — з нового виміру.
// alpha_num/alpha_den ≈ частка нового (напр. 1/8). Жорстке — лише при першому захопленні.
void on_time_mark_soft(uint64_t capture_us) {
    if (!g_synced) {                  // перший захоп — ставимо як є
        g_epoch_us = capture_us;
        g_synced   = true;
    } else {
        // де МАВ би бути цей маяк за нашим розкладом — найближчий край кадру
        uint64_t expected = nearest_frame_edge(capture_us);
        int64_t  err      = (int64_t)(capture_us - expected);   // похибка, мкс (±)
        g_epoch_us += err / 8;        // тягнемо T₀ на 1/8 похибки — згладжуємо шум
    }
    g_last_mark_us = capture_us;
}

// Найближчий до t край кадру за нашим поточним T₀ (щоб порівняти вимір з очікуванням).
static uint64_t nearest_frame_edge(uint64_t t) {
    uint64_t since = t - g_epoch_us;
    uint64_t k     = (since + FRAME_US / 2) / FRAME_US;   // округлення до найближчого кадру
    return g_epoch_us + k * FRAME_US;
}
