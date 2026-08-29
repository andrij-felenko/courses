/* supervisor.c — вимірювання середовища й рішення, що вимкнути першим. */

#include <math.h>

#include "platform.h"
#include "supervisor.h"

/* Дільник температури: 10 кОм від опорної напруги до вузла, NTC від вузла
 * на землю. Паспорт термістора: 10 кОм при +25 °C, β = 3435 K. */
#define NTC_TOP_OHM 10000.0f
#define NTC_R25_OHM 10000.0f
#define NTC_BETA_K 3435.0f
#define KELVIN_25 298.15f

#define VBAT_DIVIDER 2u /* 100к/100к: на ніжці рівно половина напруги */

static bool read_temperature(int16_t *out)
{
    uint16_t counts = 0u;
    if (!plat_adc_read(PLAT_ADC_CH_NTC, &counts)) {
        return false;
    }

    /* Нуль і повна шкала — це не −60 °C і не +200 °C, а обрив дільника
     * чи замикання термістора. Віддавати таке як температуру означає
     * дати супервізору команду вимкнути все або не вмикати нічого. */
    if (counts == 0u || counts >= PLAT_ADC_FULL_SCALE) {
        return false;
    }

    const float r_ntc = NTC_TOP_OHM * (float)counts / (float)(PLAT_ADC_FULL_SCALE - counts);
    const float inv_t = 1.0f / KELVIN_25 + logf(r_ntc / NTC_R25_OHM) / NTC_BETA_K;
    const float celsius = 1.0f / inv_t - 273.15f;

    *out = (int16_t)(celsius + (celsius >= 0.0f ? 0.5f : -0.5f));
    return true;
}

static bool read_voltage(uint16_t *out)
{
    uint16_t counts = 0u;
    if (!plat_adc_read(PLAT_ADC_CH_VBAT, &counts)) {
        return false;
    }
    const uint32_t mv = ((uint32_t)counts * PLAT_ADC_VREF_MV) / PLAT_ADC_FULL_SCALE;
    *out = (uint16_t)(mv * VBAT_DIVIDER);
    return true;
}

bool supervisor_sample(field_sample_t *out)
{
    if (out == 0) {
        return false;
    }
    out->temp_c = 0;
    out->vbat_mv = 0u;
    out->temp_valid = read_temperature(&out->temp_c);
    out->volt_valid = read_voltage(&out->vbat_mv);
    return out->temp_valid || out->volt_valid;
}

/* --- застосування стану -------------------------------------------------- */

static void apply_thermal(supervisor_t *sup, sup_thermal_t state)
{
    if (sup->thermal == state) {
        return;
    }
    sup->thermal = state;

    switch (state) {
    case SUP_THERMAL_NOMINAL:
        plat_set_core_divider(0u); /* 168 МГц */
        break;
    case SUP_THERMAL_THROTTLED:
        /* Половина частоти — це приблизно половина динамічного споживання
         * ядра, тобто менше тепла в корпусі, який і так не встигає його
         * віддати. Радіо при цьому мовчить: його імпульс гріє найдужче. */
        plat_set_core_divider(1u); /* 84 МГц */
        plat_load_set(PLAT_LOAD_RADIO, false);
        break;
    case SUP_THERMAL_CRITICAL:
    default:
        plat_set_core_divider(2u); /* 42 МГц */
        plat_load_set(PLAT_LOAD_RADIO, false);
        plat_load_set(PLAT_LOAD_HEATER, false);
        plat_load_set(PLAT_LOAD_CHARGER, false);
        break;
    }
}

static void thermal_step(supervisor_t *sup, int16_t temp_c)
{
    switch (sup->thermal) {
    case SUP_THERMAL_NOMINAL:
        if (temp_c >= SUP_TEMP_CRITICAL_C) {
            apply_thermal(sup, SUP_THERMAL_CRITICAL);
        } else if (temp_c >= SUP_TEMP_THROTTLE_ON_C) {
            apply_thermal(sup, SUP_THERMAL_THROTTLED);
        }
        break;
    case SUP_THERMAL_THROTTLED:
        if (temp_c >= SUP_TEMP_CRITICAL_C) {
            apply_thermal(sup, SUP_THERMAL_CRITICAL);
        } else if (temp_c <= SUP_TEMP_THROTTLE_OFF_C) {
            apply_thermal(sup, SUP_THERMAL_NOMINAL);
        }
        break;
    case SUP_THERMAL_CRITICAL:
    default:
        if (temp_c <= SUP_TEMP_CRITICAL_OFF_C) {
            apply_thermal(sup, SUP_THERMAL_THROTTLED);
        }
        break;
    }
}

static void cold_step(supervisor_t *sup, const field_sample_t *sample)
{
    const int16_t t = sample->temp_c;

    /* Заряд нижче нуля не «небажаний», а заборонений: іони літію не
     * встигають увійти в графіт і осідають на аноді металевими голками,
     * які проростають крізь сепаратор. Це відкладена пожежа, і жодна
     * вигода від дозарядки її не варта. */
    if (t <= SUP_TEMP_CHARGE_BLOCK_C) {
        sup->charge_blocked = true;
    } else if (t >= SUP_TEMP_CHARGE_ALLOW_C) {
        sup->charge_blocked = false;
    }
    plat_load_set(PLAT_LOAD_CHARGER,
                  !sup->charge_blocked && sup->thermal != SUP_THERMAL_CRITICAL);

    /* Підігрів сам споживає струм, тому вмикається лише коли джерело
     * тримає напругу: інакше на морозі він же й посадить шину. */
    const bool supply_ok = sample->volt_valid && sample->vbat_mv >= SUP_VOLT_OK_MV;
    if (!supply_ok || sup->thermal == SUP_THERMAL_CRITICAL) {
        sup->heater_on = false;
    } else if (t <= SUP_TEMP_HEATER_ON_C) {
        sup->heater_on = true;
    } else if (t >= SUP_TEMP_HEATER_OFF_C) {
        sup->heater_on = false;
    }
    plat_load_set(PLAT_LOAD_HEATER, sup->heater_on);
}

static void supply_step(supervisor_t *sup, uint16_t mv)
{
    if (plat_load_get(PLAT_LOAD_RADIO)) {
        if (mv < SUP_VOLT_SHED_MV) {
            /* Просадка під навантаженням. Знімаємо передавач негайно:
             * ще кілька десятків мілівольт — і спрацює BOR, а перезапуск
             * посеред кадру коштує дорожче за втрачений сеанс. */
            plat_load_set(PLAT_LOAD_RADIO, false);
            sup->sag_events++;

            if (sup->idle_mv > mv) {
                sup->r_int_mohm =
                    (uint16_t)(((uint32_t)(sup->idle_mv - mv) * 1000u) / SUP_RADIO_PULSE_MA);
                sup->r_int_known = true;
            }
        }
    } else {
        sup->idle_mv = mv; /* без навантаження бачимо ЕРС джерела */
    }
}

/* --- зовнішній інтерфейс ------------------------------------------------- */

void supervisor_init(supervisor_t *sup, bool safe_start, uint32_t now_ms)
{
    if (sup == 0) {
        return;
    }

    sup->thermal = SUP_THERMAL_NOMINAL;
    sup->charge_blocked = true; /* доки не побачили температуру — заряд заборонено */
    sup->heater_on = false;
    sup->blind = true;
    sup->blind_since_ms = now_ms;
    sup->idle_mv = 0u;
    sup->r_int_mohm = 0u;
    sup->r_int_known = false;
    sup->sag_events = 0u;
    sup->last_temp_c = 0;
    sup->started_ms = now_ms;

    plat_load_set(PLAT_LOAD_RADIO, false);
    plat_load_set(PLAT_LOAD_HEATER, false);
    plat_load_set(PLAT_LOAD_CHARGER, false);

    if (safe_start) {
        apply_thermal(sup, SUP_THERMAL_THROTTLED);
    }
}

void supervisor_step(supervisor_t *sup, const field_sample_t *sample, uint32_t now_ms)
{
    if (sup == 0 || sample == 0) {
        return;
    }

    if (!sample->temp_valid && !sample->volt_valid) {
        if (!sup->blind) {
            sup->blind = true;
            sup->blind_since_ms = now_ms;
        }
        /* Осліпнути на секунду — дрібниця (АЦП міг не встигнути).
         * Осліпнути надовго — означає більше не знати, у якому ми
         * середовищі, а в такому стані єдина безпечна дія — не діяти. */
        if ((uint32_t)(now_ms - sup->blind_since_ms) > SUP_BLIND_LIMIT_MS) {
            apply_thermal(sup, SUP_THERMAL_CRITICAL);
        }
        return;
    }

    sup->blind = false;

    if (sample->temp_valid) {
        sup->last_temp_c = sample->temp_c;
        thermal_step(sup, sample->temp_c);
        cold_step(sup, sample);
    }
    if (sample->volt_valid) {
        supply_step(sup, sample->vbat_mv);
    }
}

sup_radio_verdict_t supervisor_radio_acquire(supervisor_t *sup)
{
    if (sup == 0) {
        return SUP_RADIO_DENIED_BLIND;
    }
    if (sup->blind || sup->idle_mv == 0u) {
        return SUP_RADIO_DENIED_BLIND;
    }
    if (sup->thermal != SUP_THERMAL_NOMINAL) {
        return SUP_RADIO_DENIED_HOT;
    }
    if (sup->last_temp_c <= SUP_TEMP_CHARGE_BLOCK_C && sup->r_int_known &&
        sup->r_int_mohm > 300u) {
        /* На морозі внутрішній опір джерела зростає в рази. Це не «холодно»,
         * а «джерело більше не тримає двоамперний імпульс». */
        return SUP_RADIO_DENIED_COLD;
    }

    if (sup->r_int_known) {
        const uint32_t drop = ((uint32_t)SUP_RADIO_PULSE_MA * sup->r_int_mohm) / 1000u;
        if (sup->idle_mv <= drop || (uint32_t)sup->idle_mv - drop < SUP_VOLT_FLOOR_MV) {
            return SUP_RADIO_DENIED_SAG;
        }
    }

    plat_load_set(PLAT_LOAD_RADIO, true);
    return SUP_RADIO_ALLOWED;
}

void supervisor_radio_release(supervisor_t *sup)
{
    if (sup == 0) {
        return;
    }

    /* Замір під навантаженням і замір після нього дають різницю, з якої
     * прямо рахується внутрішній опір джерела. Це єдине місце, де прилад
     * може дізнатися його НЕ з паспорта, а зі свого сьогоднішнього
     * акумулятора на своєму сьогоднішньому морозі. */
    field_sample_t loaded;
    const bool loaded_ok = supervisor_sample(&loaded) && loaded.volt_valid;

    plat_load_set(PLAT_LOAD_RADIO, false);
    plat_delay_us(2000u); /* даємо шині відновитися після зняття імпульсу */

    field_sample_t idle;
    const bool idle_ok = supervisor_sample(&idle) && idle.volt_valid;

    if (loaded_ok && idle_ok && idle.vbat_mv > loaded.vbat_mv) {
        sup->idle_mv = idle.vbat_mv;
        sup->r_int_mohm =
            (uint16_t)(((uint32_t)(idle.vbat_mv - loaded.vbat_mv) * 1000u) / SUP_RADIO_PULSE_MA);
        sup->r_int_known = true;
    } else if (idle_ok) {
        sup->idle_mv = idle.vbat_mv;
    }
}

const char *supervisor_verdict_name(sup_radio_verdict_t verdict)
{
    switch (verdict) {
    case SUP_RADIO_ALLOWED:
        return "allowed";
    case SUP_RADIO_DENIED_HOT:
        return "hot";
    case SUP_RADIO_DENIED_COLD:
        return "cold";
    case SUP_RADIO_DENIED_SAG:
        return "sag";
    default:
        return "blind";
    }
}
