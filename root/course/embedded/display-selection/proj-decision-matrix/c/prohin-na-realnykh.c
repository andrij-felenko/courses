static const char *verdict_str(Verdict v)
{
    switch (v) {
    case VERDICT_FITS:            return "влазить як є";
    case VERDICT_NEED_BETTER_MCU: return "потрібен дорожчий МК";
    case VERDICT_REDUCE_RES:      return "зменшити роздільність";
    case VERDICT_OVERFLOW:        return "переповнення розрахунку";
    }
    return "?";
}

int main(void)
{
    McuSpec mcu = { .free_ram_bytes = 128u * 1024u,  /* 128 КБ */
                    .bus_clock_bps  = 40000000u };    /* SPI 40 МГц */

    /* А) 320×240 RGB565, SPI-панель із GRAM, статичний вміст ~5 к/с */
    DisplaySpec a = { 320, 240, FMT_RGB565, 5,  true  };
    /* Б) 320×240 RGB565, RGB-панель без GRAM, 60 к/с             */
    DisplaySpec b = { 320, 240, FMT_RGB565, 60, false };
    /* В) 800×480 RGB565, RGB-панель без GRAM, 60 к/с             */
    DisplaySpec c = { 800, 480, FMT_RGB565, 60, false };

    printf("А) SPI+GRAM 320×240:  %s\n", verdict_str(budget_verdict(&a, &mcu)));
    printf("Б) RGB 320×240 60fps: %s\n", verdict_str(budget_verdict(&b, &mcu)));
    printf("В) RGB 800×480 60fps: %s\n", verdict_str(budget_verdict(&c, &mcu)));
    return 0;
}
