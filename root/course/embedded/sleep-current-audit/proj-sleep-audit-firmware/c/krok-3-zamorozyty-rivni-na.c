static void freeze_pins_for_deep_sleep(void)
{
    // 1) Заморозити рівень кожної цифрової ніжки з профілю.
    for (size_t i = 0; i < SLEEP_PROFILE_LEN; i++) {
        gpio_hold_en(SLEEP_PROFILE[i].pin);   // залочити поточний (LOW/Hi-Z) стан
    }

    // 2) Увімкнути утримання цифрових ніжок саме на час deep-sleep.
    //    Без цього рядка на ESP32 п.1 не діє у глибокому сні!
    gpio_deep_sleep_hold_en();
}
