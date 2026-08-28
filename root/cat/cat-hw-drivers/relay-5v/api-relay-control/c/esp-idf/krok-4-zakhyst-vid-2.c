static int64_t last_switch = 0;                  // мить минулого РЕАЛЬНОГО перемикання
#define MIN_INTERVAL_MS 500                      // не частіше ніж раз на 0.5 с

// Безпечне перемикання: пропустить, лише якщо минув мінімальний інтервал.
// Повертає true, якщо перемикання відбулося.
bool relay_switch(bool on) {
    if (on == relay_state) return false;                    // уже в цьому стані
    if (now_ms() - last_switch < MIN_INTERVAL_MS)           // ще рано перемикати
        return false;
    relay_state = on;
    relay_write(on);
    last_switch = now_ms();
    return true;
}
