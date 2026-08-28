// Ініціалізація драйвера бази: змірятись і налаштувати компенсацію.
void base_driver_init(void)
{
    capture_setup_rising_filtered();      // захоплення на фронт Vce, з фільтром
    pwm_setup_20khz();                    // ШІМ-канал на базу

    uint32_t t_dead = measure_dead_time_median(9);   // 9 вимірів, медіана
    if (t_dead == 0) {
        fault_raise(FAULT_NO_COLLECTOR_EDGE);   // навантаження/поріг/ключ — розбір окремо
        return;
    }
    pwm_set_dead_time_ns(t_dead);         // закешувати компенсацію

    // Санітарна межа: якщо сховок з'їдає надто велику частку періоду —
    // цей ключ не годиться для такої частоти (див. рішення BJT/MOSFET нижче).
    if (t_dead > (1000000000ull * PWM_PERIOD / PWM_TIMER_HZ) / 4) {
        fault_raise(FAULT_DEAD_TIME_TOO_LARGE);   // t_dead > 25% періоду
    }
}
