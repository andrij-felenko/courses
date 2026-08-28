static void watch_realtime_offset(int seconds)
{
    struct timespec r, m;
    int64_t first, now;

    clock_gettime(CLOCK_REALTIME,  &r);
    clock_gettime(CLOCK_MONOTONIC, &m);
    first = to_ns(&r) - to_ns(&m);

    printf("стежимо %d с. Спробуйте в іншому терміналі:\n"
           "    sudo date -s \"-2 seconds\"\n", seconds);

    for (int i = 1; i <= seconds; i++) {
        sleep(1);                /* сам sleep рахує по MONOTONIC — тому й не збивається */
        clock_gettime(CLOCK_REALTIME,  &r);
        clock_gettime(CLOCK_MONOTONIC, &m);
        now = to_ns(&r) - to_ns(&m);
        printf("  %2d с: зміщення зрушило на %+.6f с\n", i, (now - first) / 1e9);
    }
}

int main(void)
{
    pin_to_current_cpu();

    puts("\n── системні годинники поруч (роздільність у нс) ──");
    show_clocks();

    puts("\n── що між ними ──");
    show_gaps();

    puts("\n── чинне джерело часу ──");
    show_clocksource();

    puts("\n── поправка від служби синхронізації ──");
    show_adjustment();

    puts("\n── ціна одного запиту часу ──");
    show_cost();

    puts("\n── чи стоїть настінний час на місці ──");
    watch_realtime_offset(5);
    return 0;
}
