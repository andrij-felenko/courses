#define SEEN_MAX     32
#define SEEN_TTL_MS  30000u        /* запис живе 30 с після останнього кадру */
#define RX_MAX       (2 * MAVLINK_MAX_PACKET_LEN)

struct seen {
    uint8_t  sys, comp;
    uint32_t last_ms;
};

struct channel {
    int          fd;
    const char  *name;
    struct seen  seen[SEEN_MAX];
    uint8_t      n_seen;
    uint8_t      rx[RX_MAX];       /* удвічі більший за найдовший кадр:    */
    size_t       rx_len;           /* «повний буфер без кадру» неможливий  */
};

static uint32_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000u + ts.tv_nsec / 1000000u);
}

/* Почули пару на цьому каналі — записати або освіжити. */
static void chan_learn(struct channel *c, uint8_t sys, uint8_t comp, uint32_t now)
{
    if (sys == 0) {
        return;        /* системи 0 не існує: адресувати їй кадр неможливо */
    }
    for (uint8_t i = 0; i < c->n_seen; i++) {
        if (c->seen[i].sys == sys && c->seen[i].comp == comp) {
            c->seen[i].last_ms = now;
            return;
        }
    }
    if (c->n_seen < SEEN_MAX) {
        c->seen[c->n_seen++] = (struct seen){ sys, comp, now };
        return;
    }
    uint8_t oldest = 0;                          /* таблиця повна —       */
    for (uint8_t i = 1; i < SEEN_MAX; i++) {     /* витісняємо найдавніший */
        if ((int32_t)(c->seen[i].last_ms - c->seen[oldest].last_ms) < 0) {
            oldest = i;
        }
    }
    c->seen[oldest] = (struct seen){ sys, comp, now };
}

/* Чи чули на каналі цю систему? comp < 0 — «будь-який її компонент». */
static bool chan_heard(const struct channel *c, uint8_t sys, int16_t comp, uint32_t now)
{
    for (uint8_t i = 0; i < c->n_seen; i++) {
        if (now - c->seen[i].last_ms > SEEN_TTL_MS) {
            continue;                            /* запис протух           */
        }
        if (c->seen[i].sys != sys) {
            continue;
        }
        if (comp < 0 || c->seen[i].comp == (uint8_t)comp) {
            return true;
        }
    }
    return false;
}
