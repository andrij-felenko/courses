// Груба кулонометрія: накопичуємо витрачений заряд у мікроампер-секундах,
// щоб не втрачати точність на малих струмах, і переводимо в мА·год за запитом.

static uint64_t spent_uas = 0;         // витрачено, мкА·с (мікроампер-секунди)
#define BATTERY_CAPACITY_MAH   2000U   // паспортна ємність комірки

// Викликається періодично (напр., раз на секунду) з поточним струмом у мкА.
void coulomb_tick(uint32_t current_ua, uint32_t dt_ms) {
    // ΔQ [мкА·с] = струм [мкА] × час [с] = current_ua × dt_ms / 1000
    spent_uas += (uint64_t)current_ua * dt_ms / 1000U;
}

// Скільки мА·год лишилось (0, якщо перебрали).
uint16_t coulomb_remaining_mah(void) {
    // 1 мА·год = 1000 мкА × 3600 с = 3 600 000 мкА·с
    uint32_t spent_mah = (uint32_t)(spent_uas / 3600000ULL);
    if (spent_mah >= BATTERY_CAPACITY_MAH) return 0;
    return (uint16_t)(BATTERY_CAPACITY_MAH - spent_mah);
}
