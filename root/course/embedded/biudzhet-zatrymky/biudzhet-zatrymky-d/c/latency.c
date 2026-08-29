#include "latency.h"

const char *lat_strerror(lat_status st)
{
    switch (st) {
    case LAT_OK:        return "гаразд";
    case LAT_ERR_FULL:  return "тракт переповнено: ланок більше за LAT_MAX_STAGES";
    case LAT_ERR_ORDER: return "хибна вилка: потрібно 0 <= min <= typ <= max";
    case LAT_ERR_RATE:  return "хибний такт: частота має бути додатною, люфт — не більшим за період";
    case LAT_ERR_LINK:  return "хибна шина: байти, біти й швидкість мають бути додатними";
    case LAT_ERR_EMPTY: return "у тракті немає ланки потрібного типу";
    }
    return "невідомий код";
}

/* Спільне тіло конструкторів. Жоден із них не звертається до купи
   й не звітує назовні — лише заповнює структуру-значення. */
static lat_stage make(const char *name, lat_kind kind,
                      double min_ms, double typ_ms, double max_ms)
{
    lat_stage st;
    st.name      = (name != NULL) ? name : "(без назви)";
    st.kind      = kind;
    st.domain    = LAT_ELECTRONIC;
    st.min_ms    = min_ms;
    st.typ_ms    = typ_ms;
    st.max_ms    = max_ms;
    st.period_ms = 0.0;
    st.synced    = false;
    st.defect    = LAT_OK;
    return st;
}

static lat_stage broken(const char *name, lat_status why)
{
    lat_stage st = make(name, LAT_FIXED, 0.0, 0.0, 0.0);
    st.defect = why;
    return st;
}

lat_stage lat_band(const char *name, double min_ms, double typ_ms, double max_ms)
{
    if (!(min_ms >= 0.0) || !(typ_ms >= min_ms) || !(max_ms >= typ_ms)) {
        /* Заперечення через ! ловить і NaN: порівняння з NaN завжди хибне. */
        return broken(name, LAT_ERR_ORDER);
    }
    return make(name, LAT_BAND, min_ms, typ_ms, max_ms);
}

lat_stage lat_fixed(const char *name, double ms)
{
    if (!(ms >= 0.0)) {
        return broken(name, LAT_ERR_ORDER);
    }
    return make(name, LAT_FIXED, ms, ms, ms);
}

lat_stage lat_periodic(const char *name, double rate_hz, bool synced, double slack_ms)
{
    lat_stage st;
    double period_ms;

    if (!(rate_hz > 0.0)) {
        return broken(name, LAT_ERR_RATE);
    }
    period_ms = 1000.0 / rate_hz;

    if (synced) {
        /* Люфт більший за період — це не фазування, а описка в конфігурації. */
        if (!(slack_ms >= 0.0) || slack_ms > period_ms) {
            return broken(name, LAT_ERR_RATE);
        }
        st = make(name, LAT_PERIODIC, slack_ms, slack_ms, slack_ms);
    } else {
        st = make(name, LAT_PERIODIC, 0.0, period_ms / 2.0, period_ms);
    }
    st.period_ms = period_ms;
    st.synced    = synced;
    return st;
}

lat_stage lat_serial(const char *name, size_t frame_bytes, double baud_bps,
                     unsigned bits_per_byte)
{
    double ms;

    if (frame_bytes == 0u || bits_per_byte == 0u || !(baud_bps > 0.0)) {
        return broken(name, LAT_ERR_LINK);
    }
    ms = (double)frame_bytes * (double)bits_per_byte * 1000.0 / baud_bps;
    return make(name, LAT_FIXED, ms, ms, ms);
}

lat_stage lat_physical(lat_stage st)
{
    st.domain = LAT_PHYSICAL;
    return st;
}

void lat_pipeline_init(lat_pipeline *p, const char *title)
{
    p->title = (title != NULL) ? title : "(тракт без назви)";
    p->count = 0u;
}

lat_status lat_pipeline_add(lat_pipeline *p, lat_stage st)
{
    if (st.defect != LAT_OK) {
        return st.defect; /* хибу зловили ще в конструкторі — не пускаємо в тракт */
    }
    if (p->count >= LAT_MAX_STAGES) {
        return LAT_ERR_FULL;
    }
    p->stages[p->count++] = st;
    return LAT_OK;
}

lat_budget lat_budget_of(const lat_pipeline *p)
{
    lat_budget b = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    size_t i;

    for (i = 0u; i < p->count; i++) {
        const lat_stage *st = &p->stages[i];
        b.min_ms += st->min_ms;
        b.typ_ms += st->typ_ms;
        b.max_ms += st->max_ms;
        if (st->domain == LAT_ELECTRONIC) {
            b.electronic_typ_ms += st->typ_ms;
        } else {
            b.physical_typ_ms += st->typ_ms;
        }
    }
    b.jitter_ms = b.max_ms - b.min_ms;
    return b;
}

lat_budget lat_budget_sum(lat_budget a, lat_budget b)
{
    lat_budget s;
    s.min_ms            = a.min_ms + b.min_ms;
    s.typ_ms            = a.typ_ms + b.typ_ms;
    s.max_ms            = a.max_ms + b.max_ms;
    s.jitter_ms         = s.max_ms - s.min_ms;
    s.electronic_typ_ms = a.electronic_typ_ms + b.electronic_typ_ms;
    s.physical_typ_ms   = a.physical_typ_ms + b.physical_typ_ms;
    return s;
}

lat_status lat_bottleneck(const lat_pipeline *p, const lat_stage **out, double *share)
{
    const lat_stage *worst = NULL;
    double total_max = 0.0;
    size_t i;

    if (p->count == 0u) {
        return LAT_ERR_EMPTY;
    }
    for (i = 0u; i < p->count; i++) {
        total_max += p->stages[i].max_ms;
        if (worst == NULL || p->stages[i].max_ms > worst->max_ms) {
            worst = &p->stages[i];
        }
    }
    *out = worst;
    if (share != NULL) {
        /* Тракт із самих нулів — вироджений, але ділити на нуль однаково не можна. */
        *share = (total_max > 0.0) ? (worst->max_ms / total_max) : 0.0;
    }
    return LAT_OK;
}

lat_status lat_worst_quantum(const lat_pipeline *p, const lat_stage **out)
{
    const lat_stage *worst = NULL;
    size_t i;

    for (i = 0u; i < p->count; i++) {
        if (p->stages[i].kind != LAT_PERIODIC) {
            continue;
        }
        if (worst == NULL || p->stages[i].period_ms > worst->period_ms) {
            worst = &p->stages[i];
        }
    }
    if (worst == NULL) {
        return LAT_ERR_EMPTY; /* суто потоковий тракт: тактових ланок немає */
    }
    *out = worst;
    return LAT_OK;
}

double lat_phase_shift_deg(double delay_ms, double control_hz)
{
    return 360.0 * control_hz * (delay_ms / 1000.0);
}

lat_pio lat_pio_verdict(double phase_deg)
{
    if (phase_deg >= 90.0) {
        return LAT_PIO_UNSTABLE;
    }
    if (phase_deg >= 45.0) {
        return LAT_PIO_WATCH;
    }
    return LAT_PIO_SAFE;
}

const char *lat_pio_text(lat_pio verdict)
{
    switch (verdict) {
    case LAT_PIO_SAFE:     return "запас за фазою є";
    case LAT_PIO_WATCH:    return "ручка «гумова», оператор перекеровує";
    case LAT_PIO_UNSTABLE: return "PIO: зворотний зв'язок став позитивним";
    }
    return "?";
}

double lat_blind_distance_m(double delay_ms, double speed_mps)
{
    return speed_mps * (delay_ms / 1000.0);
}
