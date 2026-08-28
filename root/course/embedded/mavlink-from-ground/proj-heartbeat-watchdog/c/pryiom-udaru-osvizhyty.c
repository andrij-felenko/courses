/* Події, які сторож повертає нагору — щоб інтерфейс/логіка відреагували. */
typedef enum {
    HB_EVT_NONE = 0,
    HB_EVT_DISCOVERED,   /* побачили джерело вперше */
    HB_EVT_RECOVERED,    /* мертве джерело знову озвалося */
    HB_EVT_LOST          /* джерело замовкло довше за поріг */
} hb_event_t;

/* Мінімальний зріз розібраного HEARTBEAT, який нам віддає парсер. */
typedef struct {
    uint8_t  sys, comp;
    uint8_t  type, autopilot, base_mode;
    uint32_t custom_mode;
} heartbeat_msg_t;

/*
 * Викликати на КОЖЕН прийнятий HEARTBEAT.
 * now_ms — поточний монотонний час (мс). Повертає подію для верхнього рівня.
 */
hb_event_t hb_on_heartbeat(hb_watchdog_t *wd,
                           const heartbeat_msg_t *hb,
                           uint32_t now_ms)
{
    hb_source_t *s = hb_find_or_alloc(wd, hb->sys, hb->comp);
    if (s == NULL)
        return HB_EVT_NONE;   /* таблиця повна — чесно нічого не робимо */

    hb_event_t evt = HB_EVT_NONE;

    if (!s->used) {
        /* Перша зустріч: заводимо джерело живим одразу. */
        s->used         = true;
        s->sys          = hb->sys;
        s->comp         = hb->comp;
        s->period_ms    = wd->default_period_ms;  /* поки не виміряли */
        s->state        = PRES_ALIVE;
        evt = HB_EVT_DISCOVERED;
    } else {
        /* Оцінюємо реальний період як інтервал між ударами цього джерела. */
        uint32_t dt = now_ms - s->last_seen_ms;   /* див. нижче про переповнення */
        if (dt > 0 && dt < 60000u)                 /* відсікаємо божевільні викиди */
            hb_update_period(s, dt);

        if (s->state == PRES_LOST) {
            /* Воскресіння: ОДНОГО удару досить — це і є наш гістерезис. */
            s->state = PRES_ALIVE;
            evt = HB_EVT_RECOVERED;
        }
    }

    /* У будь-якому разі — освіжаємо час і контекст мітки. */
    s->last_seen_ms = now_ms;
    s->type         = hb->type;
    s->autopilot    = hb->autopilot;
    s->base_mode    = hb->base_mode;
    s->custom_mode  = hb->custom_mode;

    return evt;
}
