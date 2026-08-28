/* Знайти слот джерела (sys,comp) або зайняти вільний. NULL — таблиця повна. */
static hb_source_t *hb_find_or_alloc(hb_watchdog_t *wd, uint8_t sys, uint8_t comp)
{
    hb_source_t *free_slot = NULL;

    for (int i = 0; i < HB_MAX_SOURCES; i++) {
        hb_source_t *s = &wd->src[i];
        if (s->used) {
            if (s->sys == sys && s->comp == comp)
                return s;                 /* уже знаємо це джерело */
        } else if (free_slot == NULL) {
            free_slot = s;                /* запам'ятали перший вільний */
        }
    }
    return free_slot;   /* нове джерело у вільний слот; NULL якщо всі зайняті */
}
