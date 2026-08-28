// Одна перевірка: cond має бути істинним. name — щоб бачити винуватця в лозі.
static void expect(int cond, const char *name) {
    tests_run++;
    if (cond) {
        uart_puts("  ok   ");
    } else {
        tests_failed++;
        uart_puts("  FAIL ");
    }
    uart_puts(name);
    uart_puts("\r\n");
}
