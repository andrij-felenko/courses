// ── Стан модуля ────────────────────────────────────────────────────────────
typedef enum { ST_DETACHED, ST_DEBOUNCING, ST_ATTACHED } state_t;

static cc_reader_cfg_t CFG;
static state_t   st       = ST_DETACHED;
static cc_line_t active   = CC_LINE_NONE;
static ring_t    ring;
static cc_level_t level   = CC_NONE;   // сталий рівень назовні
static cc_level_t cand    = CC_NONE;   // кандидат на сталий
static uint8_t    cand_n  = 0;         // скільки разів кандидат повторився

static void emit(cc_event_t ev) {       // безпечно віддати подію назовні
    if (CFG.on_event) CFG.on_event(ev, level, CFG.user);
}

static void go_detached(void) {         // спільний відкат у «нема джерела»
    bool was_attached = (st == ST_ATTACHED);
    st = ST_DETACHED;
    active = CC_LINE_NONE;
    level = CC_NONE; cand = CC_NONE; cand_n = 0;
    ring_reset(&ring);                  // чистимо буфер під наступне під'єднання
    if (was_attached) emit(CC_EV_DETACHED);  // подію — лише якщо реально від'єднались
}

void cc_reader_init(const cc_reader_cfg_t *cfg) {
    CFG = *cfg;
    ring_reset(&ring);
    st = ST_DETACHED; active = CC_LINE_NONE;
    level = CC_NONE; cand = CC_NONE; cand_n = 0;
}
