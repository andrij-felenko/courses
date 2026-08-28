static uint32_t last_switch = 0;                 // мить минулого РЕАЛЬНОГО перемикання
#define MIN_INTERVAL_MS 500u                     // не частіше ніж раз на 0.5 с

// Безпечне перемикання: пропустить, лише якщо минув мінімальний інтервал.
// Повертає true, якщо перемикання відбулося.
bool relay_switch(bool on) {
    if (on == relay_state) return false;                    // уже в цьому стані
    if ((HAL_GetTick() - last_switch) < MIN_INTERVAL_MS)    // ще рано перемикати
        return false;
    relay_state = on;
    relay_write(on);
    last_switch = HAL_GetTick();
    return true;
}
