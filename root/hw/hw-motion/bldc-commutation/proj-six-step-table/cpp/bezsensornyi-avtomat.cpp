// Безсенсорний автомат: сектор ЖИВЕ у змінній й крокує по одному.
static volatile uint8_t g_sector = 0;      // поточний рядок 0..5
static volatile uint32_t g_last_sector_us; // тривалість минулого сектора

// Викликається з таймера рівно на МЕЖІ сектора (через 30° після нуля).
void commutation_tick(int forward) {
    g_sector = forward ? (uint8_t)((g_sector + 1) % 6)
                       : (uint8_t)((g_sector + 5) % 6);   // +5 ≡ −1 (mod 6)
    apply_inverter(STEP_FWD[forward ? g_sector : (5 - g_sector)]);
}

// Викликається компаратором, коли ЕРС вільної фази перетнула нуль.
void on_zero_crossing(uint32_t now_us) {
    static uint32_t prev_zc_us = 0;
    g_last_sector_us = now_us - prev_zc_us;   // час між двома нулями = сектор
    prev_zc_us = now_us;
    // чекати 30° = пів сектора, тоді commutation_tick():
    schedule_after(g_last_sector_us / 2, commutation_tick);
}
