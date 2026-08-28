// power_monitor.c
#include "power_monitor.h"

void pm_init(pm_channel_t *ch, const pm_config_t *cfg) {
    ch->cfg = cfg;
    ch->st  = PM_OK;             // доки не доведено погане — вважаємо норму
    ch->bus_mv = 0u;
    ch->sum = 0u; ch->head = 0u; ch->count = 0u;
    for (uint8_t i = 0; i < 8; i++) ch->buf[i] = 0u;
    ch->bad_run = 0u; ch->good_run = 0u;
    ch->flag_latched = false;
}

// Сирий код АЦП → напруга шини в мілівольтах, з урахуванням дільника.
// Порядок множень навмисний: спершу *vref, тоді дільник — щоб не втратити
// точність на цілих і не переповнити 32 біти (коди й напруги невеликі).
static uint16_t code_to_bus_mv(const pm_config_t *c, uint16_t code) {
    uint32_t v_adc = (uint32_t)code * c->vref_mv / c->adc_full;   // напруга на нозі
    uint32_t v_bus = v_adc * c->div_num / c->div_den;             // назад до шини
    return (v_bus > 0xFFFFu) ? 0xFFFFu : (uint16_t)v_bus;
}

// Кільцевий буфер: один новий відлік за виклик, миттєве середнє по 8.
static uint16_t ring_avg(pm_channel_t *ch, uint16_t code) {
    ch->sum -= ch->buf[ch->head];
    ch->buf[ch->head] = code;
    ch->sum += code;
    ch->head = (ch->head + 1u) & 7u;             // & 7 == % 8 (степінь двійки)
    if (ch->count < 8u) ch->count++;
    return (uint16_t)(ch->sum / ch->count);
}
