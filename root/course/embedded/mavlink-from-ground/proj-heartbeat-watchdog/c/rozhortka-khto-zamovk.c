/*
 * Викликати періодично (напр. кожні 100–200 мс) з циклу станції.
 * Проходить джерела й переводить у LOST ті, що мовчать довше за поріг.
 * Події (LOST) віддаємо через колбек, бо їх може бути кілька за один прохід.
 */
typedef void (*hb_event_cb)(const hb_source_t *s, hb_event_t evt, void *user);

void hb_tick(hb_watchdog_t *wd, uint32_t now_ms, hb_event_cb cb, void *user)
{
    for (int i = 0; i < HB_MAX_SOURCES; i++) {
        hb_source_t *s = &wd->src[i];
        if (!s->used || s->state != PRES_ALIVE)
            continue;   /* цікавлять лише живі — мертвих уже полічили */

        uint32_t silence   = now_ms - s->last_seen_ms;   /* скільки мовчить */
        uint32_t threshold = (uint32_t)wd->miss_to_lose * s->period_ms;

        if (silence > threshold) {
            s->state = PRES_LOST;               /* мітку — гасити */
            if (cb) cb(s, HB_EVT_LOST, user);   /* тривогу — нагору */
        }
    }
}
