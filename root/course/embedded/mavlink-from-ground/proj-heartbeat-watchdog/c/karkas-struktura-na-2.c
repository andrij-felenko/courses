#define HB_MAX_SOURCES   8   /* стільки різних (SYS,COMP) тримаємо водночас */

typedef struct {
    hb_source_t src[HB_MAX_SOURCES];
    /* пороги — параметри, а не магічні числа в коді */
    uint8_t  miss_to_lose;   /* скільки пропущених ударів = «втрачено» */
    uint32_t default_period_ms; /* період, поки не оцінили реальний */
} hb_watchdog_t;

void hb_init(hb_watchdog_t *wd)
{
    for (int i = 0; i < HB_MAX_SOURCES; i++)
        wd->src[i].used = false;
    wd->miss_to_lose      = 4;      /* N = 4 пропущені удари */
    wd->default_period_ms = 1000;   /* поки не виміряли — 1 Гц */
}
