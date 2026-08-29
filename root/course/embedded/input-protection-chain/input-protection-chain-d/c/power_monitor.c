/* power_monitor.c — фільтр, перерахунок у вольти й автомат станів захисту. */
#include <stddef.h>

#include "power_monitor.h"

/* Різниця часу як знакова: (int32_t)(a - b) >= 0 переживає переповнення
 * лічильника мілісекунд, а пряме порівняння a >= b — ні. */
static bool time_reached(uint32_t now_ms, uint32_t deadline_ms)
{
    return (int32_t)(now_ms - deadline_ms) >= 0;
}

static bool config_sane(const pwr_config_t *c)
{
    if (c->div_bottom_ohm == 0U || c->adc_full_scale == 0U || c->vref_mv == 0U) return false;
    if (c->filter_shift > 15U) return false;
    if (c->confirm_samples == 0U || c->settle_samples == 0U) return false;
    /* Пороги мусять іти зростаючим рядом, інакше гістерезис вивернеться. */
    if (!(c->uvlo_trip_mv < c->uvlo_clear_mv &&
          c->uvlo_clear_mv < c->ovlo_clear_mv &&
          c->ovlo_clear_mv < c->ovlo_trip_mv)) return false;
    return true;
}

static void set_output(pwr_monitor_t *mon, bool on)
{
    if (mon->enabled == on) return;
    mon->enabled = on;
    if (mon->set_enable) mon->set_enable(mon->ctx, on);
}

/* Код АЦП → мілівольти шини. Ділимо один раз: два послідовні цілочислові
 * ділення втратили б до півтора відсотка на краю шкали. */
static uint32_t code_to_bus_mv(const pwr_config_t *c, uint32_t code)
{
    uint64_t num = (uint64_t)code * c->vref_mv * ((uint64_t)c->div_top_ohm + c->div_bottom_ohm);
    uint64_t den = (uint64_t)c->adc_full_scale * c->div_bottom_ohm;
    return (uint32_t)(num / den);
}

/* Експоненційне згладжування у Q8: y += (x - y) >> shift. */
static uint32_t filter_step(pwr_monitor_t *mon, uint16_t code)
{
    uint32_t sample_q8 = (uint32_t)code << 8;

    if (!mon->primed) {
        /* Перша вибірка заряджає фільтр цілком: інакше ввімкнення виглядало б
         * як просідання, і захист відрапортував би про аварію на порожньому місці.
         * Ознакою «фільтр порожній» служить окремий прапорець, а не нуль у стані:
         * нуль — цілком законне свідчення знеструмленої шини. */
        mon->filtered_q8 = sample_q8;
        mon->primed = true;
    } else {
        int32_t diff = (int32_t)sample_q8 - (int32_t)mon->filtered_q8;
        mon->filtered_q8 = (uint32_t)((int32_t)mon->filtered_q8 + (diff >> mon->cfg.filter_shift));
    }
    return mon->filtered_q8 >> 8;
}

/* Знімає прапорець аварії, виставлений перериванням. Гонка тут коштує щонайбільше
 * повторного сигналу тієї самої аварії: сам факт уже пішов у обробку. */
static bool take_efuse_flag(pwr_monitor_t *mon)
{
    if (mon->efuse_flag == 0U) return false;
    mon->efuse_flag = 0U;
    return true;
}

static bool inside_window(const pwr_monitor_t *mon)
{
    return mon->voltage_mv >= mon->cfg.uvlo_clear_mv &&
           mon->voltage_mv <= mon->cfg.ovlo_clear_mv;
}

static void count_fault(pwr_monitor_t *mon, pwr_state_t fault)
{
    switch (fault) {
        case PWR_FAULT_UVLO:  mon->stats.uvlo_events++;  break;
        case PWR_FAULT_OVLO:  mon->stats.ovlo_events++;  break;
        case PWR_FAULT_EFUSE: mon->stats.efuse_events++; break;
        default: break;
    }
}

/* Спільний вхід в аварію: розмикаємо ключ, рахуємо подію й вирішуємо,
 * чи лишився ще дозволений повтор. */
static void enter_fault(pwr_monitor_t *mon, pwr_state_t fault, uint32_t now_ms)
{
    set_output(mon, false);
    mon->confirm_count = 0U;
    mon->settle_count = 0U;
    mon->pending_fault = PWR_OFF;
    mon->last_fault_ms = now_ms;
    count_fault(mon, fault);

    if (mon->cfg.retry_limit != 0U && mon->retries_used >= mon->cfg.retry_limit) {
        /* Повтори вичерпано: далі це вже не перехідний процес, а несправність. */
        mon->state = PWR_LOCKOUT;
        mon->stats.lockouts++;
        return;
    }

    mon->retries_used++;
    mon->state = fault;
    mon->retry_at_ms = now_ms + mon->cfg.retry_delay_ms;
}

pwr_err_t pwr_monitor_init(pwr_monitor_t *mon,
                           const pwr_config_t *cfg,
                           void (*set_enable)(void *ctx, bool on),
                           void *ctx)
{
    if (!mon || !cfg) return PWR_ERR_ARG;
    if (!config_sane(cfg)) return PWR_ERR_CONFIG;

    const pwr_monitor_t blank = {0};
    *mon = blank;
    mon->cfg = *cfg;
    mon->set_enable = set_enable;
    mon->ctx = ctx;
    mon->state = PWR_OFF;
    mon->pending_fault = PWR_OFF;
    mon->stats.v_min_mv = UINT32_MAX;

    /* Ключ розмикаємо ще до першої вибірки: поки напруга не виміряна,
     * дозволяти живлення нема підстав. */
    mon->enabled = true;
    set_output(mon, false);
    return PWR_OK;
}

void pwr_monitor_efuse_isr(pwr_monitor_t *mon)
{
    if (!mon) return;
    mon->efuse_flag = 1U;
}

pwr_err_t pwr_monitor_on_sample(pwr_monitor_t *mon, uint16_t adc_code, uint32_t now_ms)
{
    if (!mon) return PWR_ERR_ARG;

    /* Насичення АЦП — не помилка вимірювання, а законний стан: 48 В на вході
     * дають на дільнику 4 В при опорних 3.3 В, і код упирається в стелю. */
    if (adc_code > mon->cfg.adc_full_scale) adc_code = (uint16_t)mon->cfg.adc_full_scale;

    uint32_t averaged = filter_step(mon, adc_code);
    mon->voltage_mv = code_to_bus_mv(&mon->cfg, averaged);

    mon->stats.samples++;
    if (mon->voltage_mv < mon->stats.v_min_mv) mon->stats.v_min_mv = mon->voltage_mv;
    if (mon->voltage_mv > mon->stats.v_max_mv) mon->stats.v_max_mv = mon->voltage_mv;

    /* Апаратна аварія б'є всі стани, крім засува: eFuse уже розімкнув вихід
     * сам, прошивці лишається не заперечувати й зафіксувати подію. */
    if (take_efuse_flag(mon) && mon->state != PWR_LOCKOUT) {
        enter_fault(mon, PWR_FAULT_EFUSE, now_ms);
        return PWR_OK;
    }

    switch (mon->state) {
        case PWR_OFF:
            if (inside_window(mon)) {
                mon->settle_count = 0U;
                mon->state = PWR_SETTLING;
            }
            break;

        case PWR_SETTLING:
            if (!inside_window(mon)) {
                mon->settle_count = 0U;
                mon->state = PWR_OFF;
                break;
            }
            if (++mon->settle_count >= mon->cfg.settle_samples) {
                mon->settle_count = 0U;
                mon->confirm_count = 0U;
                set_output(mon, true);
                mon->stats.starts++;
                mon->state = PWR_ON;
            }
            break;

        case PWR_ON: {
            pwr_state_t fault = PWR_OFF;
            if (mon->voltage_mv < mon->cfg.uvlo_trip_mv)      fault = PWR_FAULT_UVLO;
            else if (mon->voltage_mv > mon->cfg.ovlo_trip_mv) fault = PWR_FAULT_OVLO;

            if (fault == PWR_OFF) {
                mon->confirm_count = 0U;
                mon->pending_fault = PWR_OFF;
                /* Довга тиша означає, що аварії були перехідними, а не серією. */
                if (mon->retries_used != 0U &&
                    time_reached(now_ms, mon->last_fault_ms + mon->cfg.retry_window_ms)) {
                    mon->retries_used = 0U;
                }
                break;
            }

            /* Одна вибірка нічого не доводить: голку від комутації сусіднього
             * навантаження фільтр не встигає з'їсти цілком. */
            if (fault != mon->pending_fault) {
                mon->pending_fault = fault;
                mon->confirm_count = 0U;
            }
            if (++mon->confirm_count >= mon->cfg.confirm_samples) {
                enter_fault(mon, fault, now_ms);
            }
            break;
        }

        case PWR_FAULT_UVLO:
        case PWR_FAULT_OVLO:
        case PWR_FAULT_EFUSE:
            if (time_reached(now_ms, mon->retry_at_ms)) {
                mon->state = PWR_OFF;  /* далі звичайний шлях OFF → SETTLING → ON */
            }
            break;

        case PWR_LOCKOUT:
            /* Виходу нема: лише pwr_monitor_clear_lockout(). */
            break;
    }

    return PWR_OK;
}

bool pwr_monitor_clear_lockout(pwr_monitor_t *mon, uint32_t now_ms)
{
    if (!mon || mon->state != PWR_LOCKOUT) return false;
    mon->retries_used = 0U;
    mon->confirm_count = 0U;
    mon->settle_count = 0U;
    mon->pending_fault = PWR_OFF;
    mon->last_fault_ms = now_ms;
    mon->state = PWR_OFF;
    return true;
}

pwr_state_t pwr_monitor_state(const pwr_monitor_t *mon)
{
    return mon ? mon->state : PWR_LOCKOUT;
}

uint32_t pwr_monitor_voltage_mv(const pwr_monitor_t *mon)
{
    return mon ? mon->voltage_mv : 0U;
}

bool pwr_monitor_output_enabled(const pwr_monitor_t *mon)
{
    return mon ? mon->enabled : false;
}

const pwr_stats_t *pwr_monitor_stats(const pwr_monitor_t *mon)
{
    return mon ? &mon->stats : NULL;
}

const char *pwr_state_name(pwr_state_t state)
{
    switch (state) {
        case PWR_OFF:         return "OFF";
        case PWR_SETTLING:    return "SETTLING";
        case PWR_ON:          return "ON";
        case PWR_FAULT_UVLO:  return "FAULT_UVLO";
        case PWR_FAULT_OVLO:  return "FAULT_OVLO";
        case PWR_FAULT_EFUSE: return "FAULT_EFUSE";
        case PWR_LOCKOUT:     return "LOCKOUT";
    }
    return "?";
}
