#include "failsafe.h"

/* ---------------------------------------------------------------------
 * Таблиця пріоритетів.
 *
 * Правило спрацьовує, коли всі біти require підтверджені й жодного з
 * forbid немає. Перше збіжне правило й дає дію, тому порядок рядків — це
 * і є ієрархія. Умова forbid існує заради GNSS: майже кожна відмова має
 * дві відповіді — з супутниками повертаємося, без них сідаємо на місці.
 * ------------------------------------------------------------------- */
typedef struct {
    uint32_t    require;
    uint32_t    forbid;
    fs_action_t action;
} fs_rule_t;

static const fs_rule_t FS_MATRIX[] = {
    /* 1. Орієнтація втрачена: керувати нічим, апарат уже некерований */
    { FS_FAULT_ATTITUDE_LOSS, 0u,                   FS_ACTION_TERMINATE },
    /* 2. Відмова приводу: тяги вистачає лише на спуск, не на маршрут */
    { FS_FAULT_ACTUATOR,      0u,                   FS_ACTION_LAND },
    /* 3. Критичний розряд: енергії на повернення вже немає */
    { FS_FAULT_BATT_CRIT,     0u,                   FS_ACTION_LAND },
    /* 4-5. Порушення геозони: назад за навігацією або вниз на межі */
    { FS_FAULT_GEOFENCE,      FS_FAULT_GNSS_GLITCH, FS_ACTION_RTL },
    { FS_FAULT_GEOFENCE,      0u,                   FS_ACTION_LAND },
    /* 6-7. Перший поріг батареї: ще встигаємо додому */
    { FS_FAULT_BATT_LOW,      FS_FAULT_GNSS_GLITCH, FS_ACTION_RTL },
    { FS_FAULT_BATT_LOW,      0u,                   FS_ACTION_LAND },
    /* 8-9. Втрата пульта: без оператора апарат летить сам */
    { FS_FAULT_RC_LOST,       FS_FAULT_GNSS_GLITCH, FS_ACTION_RTL },
    { FS_FAULT_RC_LOST,       0u,                   FS_ACTION_LAND },
    /* 10. Самотній збій GNSS: пульт у руках, тримаємо висоту */
    { FS_FAULT_GNSS_GLITCH,   0u,                   FS_ACTION_ALTHOLD },
    /* 11. Немає телеметрії — оператор бачить апарат очима, лише сигнал */
    { FS_FAULT_GCS_LOST,      0u,                   FS_ACTION_WARN },
    /* 12. Порожня вимога збігається завжди — норма */
    { 0u,                     0u,                   FS_ACTION_NONE }
};

fs_config_t fs_config_default(void)
{
    fs_config_t cfg = {0};
    cfg.debounce_ms[FS_BIT_RC_LOST]       = 1500u;
    cfg.debounce_ms[FS_BIT_GCS_LOST]      = 5000u;
    cfg.debounce_ms[FS_BIT_GNSS_GLITCH]   = 3000u;
    cfg.debounce_ms[FS_BIT_BATT_LOW]      = 1000u;
    cfg.debounce_ms[FS_BIT_BATT_CRIT]     = 1000u;
    cfg.debounce_ms[FS_BIT_GEOFENCE]      =  500u;
    cfg.debounce_ms[FS_BIT_ACTUATOR]      =    0u; /* без фільтрації */
    cfg.debounce_ms[FS_BIT_ATTITUDE_LOSS] =    0u; /* без фільтрації */
    cfg.action_hold_ms = 500u;
    return cfg;
}

const char *fs_action_name(fs_action_t action)
{
    switch (action) {
    case FS_ACTION_NONE:      return "NONE";
    case FS_ACTION_WARN:      return "WARN";
    case FS_ACTION_ALTHOLD:   return "ALTHOLD";
    case FS_ACTION_RTL:       return "RTL";
    case FS_ACTION_LAND:      return "LAND";
    case FS_ACTION_TERMINATE: return "TERMINATE";
    }
    return "?";
}

const char *fs_fault_name(unsigned bit)
{
    static const char *const names[FS_FAULT_COUNT] = {
        "RC_LOST", "GCS_LOST", "GNSS_GLITCH", "BATT_LOW",
        "BATT_CRIT", "GEOFENCE", "ACTUATOR", "ATTITUDE_LOSS"
    };
    return (bit < FS_FAULT_COUNT) ? names[bit] : "?";
}

/* ---- Поштова скринька ------------------------------------------------ */

void fs_inbox_init(fs_inbox_t *box)
{
    atomic_init(&box->bits, 0u);
}

void fs_report_fault(fs_inbox_t *box, uint32_t flags, bool active)
{
    /* Атомарні or/and замість читання-модифікації-запису: драйвер може
     * смикнути свій біт із переривання посеред нашого такту. */
    if (active) {
        atomic_fetch_or_explicit(&box->bits, flags, memory_order_release);
    } else {
        atomic_fetch_and_explicit(&box->bits, ~flags, memory_order_release);
    }
}

uint32_t fs_inbox_snapshot(const fs_inbox_t *box)
{
    /* Знімок робиться один раз на такт: усі правила таблиці мусять
     * дивитися на ту саму маску, інакше рішення буде з двох різних світів. */
    return atomic_load_explicit(&box->bits, memory_order_acquire);
}

/* ---- Арбітр ---------------------------------------------------------- */

static void reset_timers(fs_state_t *st)
{
    for (unsigned i = 0; i < FS_FAULT_COUNT; ++i) {
        st->start_ms[i] = 0u;
        st->running[i]  = false;
    }
    st->confirmed = 0u;
}

void fs_arbiter_init(fs_state_t *st, const fs_config_t *cfg)
{
    st->cfg             = *cfg;
    st->action          = FS_ACTION_NONE;
    st->action_since_ms = 0u;
    st->armed           = false;
    reset_timers(st);
}

void fs_arbiter_preflight_done(fs_state_t *st, uint32_t now_ms)
{
    reset_timers(st);
    st->action          = FS_ACTION_NONE;
    st->action_since_ms = now_ms;
    st->armed           = true;
}

void fs_arbiter_disarm(fs_state_t *st)
{
    reset_timers(st);
    st->action = FS_ACTION_NONE;
    st->armed  = false;
}

bool fs_arbiter_operator_ack(fs_state_t *st, uint32_t now_ms)
{
    if (st->action == FS_ACTION_TERMINATE) {
        return false; /* з термінації в польоті виходу немає */
    }
    st->action          = FS_ACTION_NONE;
    st->action_since_ms = now_ms;
    /* Підтверджену маску не чіпаємо: якщо відмова досі жива, наступний
     * такт підніме ту саму дію негайно — і це правильно. */
    return true;
}

fs_action_t fs_matrix_action(uint32_t confirmed_faults)
{
    for (unsigned i = 0; i < sizeof(FS_MATRIX) / sizeof(FS_MATRIX[0]); ++i) {
        const fs_rule_t *r = &FS_MATRIX[i];
        if ((confirmed_faults & r->require) == r->require &&
            (confirmed_faults & r->forbid) == 0u) {
            return r->action;
        }
    }
    return FS_ACTION_NONE; /* недосяжно: останнє правило порожнє */
}

fs_action_t fs_arbiter_update(fs_state_t *st, uint32_t raw_faults, uint32_t now_ms)
{
    if (!st->armed) {
        /* Фаза калібрування: сенсори ще брешуть, рішень не приймаємо. */
        reset_timers(st);
        st->action = FS_ACTION_NONE;
        return FS_ACTION_NONE;
    }

    raw_faults &= FS_FAULT_ALL; /* біти поза словником — не наша справа */

    /* 1. Часова фільтрація: аномалія стає відмовою, лише переживши поріг */
    for (unsigned i = 0; i < FS_FAULT_COUNT; ++i) {
        const uint32_t flag = 1u << i;
        if (raw_faults & flag) {
            if (!st->running[i]) {
                st->running[i]  = true;
                st->start_ms[i] = now_ms;
            }
            /* Різниця беззнакова, тож переповнення лічильника мілісекунд
             * (кожні ~49 діб) порівняння не ламає. */
            if ((uint32_t)(now_ms - st->start_ms[i]) >= st->cfg.debounce_ms[i]) {
                st->confirmed |= flag;
            }
        } else {
            st->running[i] = false;
            st->confirmed &= ~flag; /* канал ожив — відмова знята */
        }
    }

    /* 2. Арбітраж: суперечливі вимоги зводить одна таблиця */
    const fs_action_t want = fs_matrix_action(st->confirmed);

    /* 3. Одностороннє підвищення суворості: назад — лише за командою
     *    оператора або після зняття з охорони. Інакше апарат вискакував би
     *    із посадки щоразу, коли напруга підстрибне на десяток мілівольт. */
    if (want <= st->action) {
        return st->action;
    }

    /* 4. Квант часу між змінами дії: не даємо контурам PID суперечливих
     *    команд поспіль. Термінація — виняток, вона не чекає нікого; так
     *    само не чекає перший вихід зі штатного режиму. */
    if (want != FS_ACTION_TERMINATE && st->action != FS_ACTION_NONE &&
        (uint32_t)(now_ms - st->action_since_ms) < st->cfg.action_hold_ms) {
        return st->action;
    }

    st->action          = want;
    st->action_since_ms = now_ms;
    return st->action;
}

uint32_t fs_arbiter_confirmed(const fs_state_t *st)
{
    return st->confirmed;
}

fs_action_t fs_arbiter_action(const fs_state_t *st)
{
    return st->action;
}
