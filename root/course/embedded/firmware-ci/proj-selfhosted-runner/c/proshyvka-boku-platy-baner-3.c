int main(void) {
    uart_init(115200);          // та сама швидкість, що й раннер відкриє
    uart_puts(HIL_BANNER "\r\n"); // ← знак життя: «дійшов до main, слухай далі»

    // Прогін усіх on-target тестів.
    test_packet_layout();
    test_timer_real_ticks();
    // ... сюди чіпляються решта перевірок, яким потрібне справжнє залізо

    // Підсумковий вердикт машинним рядком.
    if (tests_failed == 0) {
        uart_puts(HIL_PASS "\r\n");
    } else {
        // Друкуємо число провалів услід за префіксом: "RESULT: FAIL 3".
        char n[12];
        uint32_t v = tests_failed, i = 0;
        if (v == 0) n[i++] = '0';
        char tmp[12]; uint32_t j = 0;
        while (v) { tmp[j++] = (char)('0' + v % 10); v /= 10; }
        while (j) n[i++] = tmp[--j];
        n[i] = '\0';
        uart_puts(HIL_FAIL);
        uart_puts(n);
        uart_puts("\r\n");
    }

    // Прошивка не завершується — вона висить, доки раннер не зробить фізичний
    // скид перед наступним прогоном. Так порт лишається відкритим для читання.
    for (;;) { /* чекаємо на скид ззовні */ }
}
