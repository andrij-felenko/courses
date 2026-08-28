static void show_clocksource(void)
{
    static const char *files[] = { "current_clocksource", "available_clocksource" };

    for (size_t i = 0; i < 2; i++) {
        char path[256], buf[256];
        FILE *f;

        snprintf(path, sizeof path,
                 "/sys/devices/system/clocksource/clocksource0/%s", files[i]);

        if ((f = fopen(path, "r")) == NULL) {
            printf("%-22s : недоступно (%s)\n", files[i], strerror(errno));
            continue;
        }
        if (fgets(buf, sizeof buf, f) != NULL) {
            buf[strcspn(buf, "\n")] = '\0';
            printf("%-22s : %s\n", files[i], buf);
        }
        fclose(f);
    }
}

static void show_adjustment(void)
{
    static const char *STATE[] = {
        "TIME_OK — синхронізовано",
        "TIME_INS — наприкінці доби вставлять секунду",
        "TIME_DEL — наприкінці доби викинуть секунду",
        "TIME_OOP — вставляння секунди триває саме зараз",
        "TIME_WAIT — вставляння щойно завершилося",
        "TIME_ERROR — годинник не синхронізовано",
    };
    struct timex tx;
    int state;
    double ppm;

    memset(&tx, 0, sizeof tx);       /* modes = 0 — лише читаємо, прав не треба */

    if ((state = adjtimex(&tx)) < 0) { perror("adjtimex"); return; }

    /* freq — це ppm, помножене на 2¹⁶: одиниця в цьому полі це 2⁻¹⁶ ppm. */
    ppm = tx.freq / 65536.0;

    printf("стан               : %s\n",
           state <= TIME_ERROR ? STATE[state] : "невідомий");
    printf("поправка швидкости : %+.3f ppm  (%+.3f с за добу)\n",
           ppm, ppm * 86400e-6);
    printf("залишок розбіжности: %+lld %s\n", (long long)tx.offset,
           (tx.status & STA_NANO) ? "нс" : "мкс");
    printf("зміщення TAI       : %d с\n", tx.tai);
}
