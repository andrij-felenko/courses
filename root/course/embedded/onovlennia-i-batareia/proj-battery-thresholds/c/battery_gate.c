#include "battery_gate.h"

#include <string.h>

/* Латч у backup-домені: один 32-бітний регістр, що живиться від RTC
   і переживає Brownout Reset. Біт «зведено» ставимо ПЕРЕД імпульсом. */
#define LATCH_MAGIC        0xB7u
#define LATCH_MAGIC_SHIFT  24
#define LATCH_ARMED_BIT    0x00000001u
#define LATCH_FAULT_SHIFT  8
#define LATCH_FAULT_MASK   0x0000FF00u

/* Часова розкладка тестового імпульсу: 12 мс на затухання перехідних
   процесів, далі 8 відліків по 250 мкс (це якраз 12–14-та мілісекунда),
   хвіст до повних 15 мс і пауза релаксації подвійного шару. */
#define PULSE_SETTLE_MS      12u
#define PULSE_SAMPLES         8u
#define PULSE_SAMPLE_GAP_US 250u
#define PULSE_TAIL_MS         1u
#define RELAX_MS             60u

const ota_limits_t OTA_LIMITS_DEFAULT = {
    .temp_min_c            = 5,
    .temp_max_c            = 45,
    .min_soc_percent       = 45,
    .v_bor_mv              = 2700,
    .bor_margin_mv         = 200,
    .test_load_ma          = 200,
    .ota_peak_ma           = 320,
    .ota_peak_throttled_ma = 175,
    .max_power_faults      = 3
};

const ota_throttle_t OTA_THROTTLE_SAFE = {
    .cpu_mhz = 40,  /* замість 160 МГц */
    .spi_mhz = 20,  /* замість 80 МГц на шині Flash */
    .tx_dbm  = 10   /* замість +20 dBm на передавачі */
};

typedef struct {
    bool    armed;
    uint8_t faults;
} latch_t;

uint16_t ota_gate_safe_floor_mv(const ota_limits_t *lim)
{
    return (uint16_t)(lim->v_bor_mv + lim->bor_margin_mv);
}

bool ota_gate_allowed(const ota_gate_report_t *report)
{
    return report != NULL && report->verdict <= OTA_ALLOW_THROTTLED;
}

const char *ota_verdict_name(ota_verdict_t verdict)
{
    switch (verdict) {
    case OTA_ALLOW_AC_POWERED: return "дозволено (зовнішнє живлення)";
    case OTA_ALLOW_BATTERY_OK: return "дозволено (батарея в нормі)";
    case OTA_ALLOW_THROTTLED:  return "дозволено (пом'якшений режим)";
    case OTA_DENY_COLD:        return "відмова: холодна комірка";
    case OTA_DENY_HOT:         return "відмова: перегріта комірка";
    case OTA_DENY_LOW_SOC:     return "відмова: замало заряду";
    case OTA_DENY_HIGH_ESR:    return "відмова: високий опір комірки";
    case OTA_DENY_POWER_FAULT: return "відмова: блокування після зривів живлення";
    case OTA_DENY_SENSOR_FAIL: return "відмова: збій вимірювальних кіл";
    }
    return "відмова: невідомий стан";
}

/* Жоден виклик у гарячій частині не перевіряє покажчик окремо — усі
   драйвери мусять бути на місці, і це питання ставиться один раз. */
static bool hal_complete(const ota_hal_t *hal)
{
    return hal->vbus_present && hal->read_temperature_c && hal->read_soc_percent
        && hal->read_voltage_mv && hal->set_test_load && hal->delay_ms
        && hal->delay_us && hal->nv_load && hal->nv_store;
}

static bool latch_load(const ota_hal_t *hal, latch_t *out)
{
    uint32_t word = 0;
    if (!hal->nv_load(hal->ctx, &word)) {
        return false;
    }
    if (((word >> LATCH_MAGIC_SHIFT) & 0xFFu) != LATCH_MAGIC) {
        /* Перше вмикання або втрачений backup-домен: рахуємо з чистого. */
        out->armed = false;
        out->faults = 0;
        return true;
    }
    out->armed  = (word & LATCH_ARMED_BIT) != 0u;
    out->faults = (uint8_t)((word & LATCH_FAULT_MASK) >> LATCH_FAULT_SHIFT);
    return true;
}

static bool latch_store(const ota_hal_t *hal, const latch_t *in)
{
    uint32_t word = ((uint32_t)LATCH_MAGIC << LATCH_MAGIC_SHIFT)
                  | ((uint32_t)in->faults << LATCH_FAULT_SHIFT)
                  | (in->armed ? LATCH_ARMED_BIT : 0u);
    return hal->nv_store(hal->ctx, word);
}

/* Серія з PULSE_SAMPLES швидких відліків із усередненням: одиничний відлік
   АЦП шумить на кілька мілівольт, а ми рахуємо різницю двох напруг. */
static bool sample_rail_mv(const ota_hal_t *hal, uint16_t *out_mv)
{
    uint32_t acc = 0;
    for (unsigned i = 0; i < PULSE_SAMPLES; ++i) {
        uint16_t mv = 0;
        if (!hal->read_voltage_mv(hal->ctx, &mv)) {
            return false;
        }
        acc += mv;
        if (i + 1u < PULSE_SAMPLES) {
            hal->delay_us(hal->ctx, PULSE_SAMPLE_GAP_US);
        }
    }
    *out_mv = (uint16_t)((acc + PULSE_SAMPLES / 2u) / PULSE_SAMPLES);
    return true;
}

/* Активний імпульсний тест. Навантаження знімається на будь-якому виході,
   включно з відмовою АЦП посеред серії. */
static bool pulse_measure(const ota_hal_t *hal, uint16_t *out_load_mv)
{
    hal->set_test_load(hal->ctx, true);
    hal->delay_ms(hal->ctx, PULSE_SETTLE_MS);

    bool ok = sample_rail_mv(hal, out_load_mv);

    hal->delay_ms(hal->ctx, PULSE_TAIL_MS);
    hal->set_test_load(hal->ctx, false);

    /* Без цієї паузи наступний замір побачить занижену напругу: подвійний
       електричний шар розсмоктується десятки мілісекунд. */
    hal->delay_ms(hal->ctx, RELAX_MS);
    return ok;
}

/* Екстраполяція просідання з тестового струму на піковий струм OTA.
   false означає, що прогнозована напруга пішла б нижче нуля. */
static bool forecast_rail_mv(uint16_t v_idle_mv,
                             uint16_t delta_test_mv,
                             uint16_t i_test_ma,
                             uint16_t i_peak_ma,
                             uint16_t *out_mv)
{
    uint32_t drop = ((uint32_t)delta_test_mv * i_peak_ma + i_test_ma / 2u) / i_test_ma;
    if (drop >= v_idle_mv) {
        *out_mv = 0;
        return false;
    }
    *out_mv = (uint16_t)(v_idle_mv - drop);
    return true;
}

static void deny(ota_gate_report_t *out, ota_verdict_t verdict)
{
    out->verdict = verdict;
}

void ota_gate_evaluate(const ota_hal_t *hal,
                       const ota_limits_t *lim,
                       bool emergency_security_fix,
                       ota_gate_report_t *out)
{
    if (out == NULL) {
        return;
    }
    memset(out, 0, sizeof(*out));

    if (hal == NULL || lim == NULL || !hal_complete(hal)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    if (lim->test_load_ma == 0u || lim->ota_peak_ma == 0u) {
        /* Зіпсована конфігурація — ділити на нуль не будемо. */
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }

    /* 0. Латч попередньої спроби. Якщо він лишився зведеним, минулий
       імпульсний тест обірвався апаратним скидом — але ДО стирання Flash,
       тож пристрій живий; просто рахуємо зрив і врешті блокуємо кампанію. */
    latch_t latch;
    if (!latch_load(hal, &latch)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    if (latch.armed) {
        if (latch.faults < UINT8_MAX) {
            latch.faults++;
        }
        latch.armed = false;
        if (!latch_store(hal, &latch)) {
            deny(out, OTA_DENY_SENSOR_FAIL);
            return;
        }
    }
    out->power_faults = latch.faults;
    if (latch.faults >= lim->max_power_faults) {
        deny(out, OTA_DENY_POWER_FAULT);
        return;
    }

    /* 1. Зовнішнє живлення знімає всі питання до комірки. */
    if (hal->vbus_present(hal->ctx)) {
        uint16_t mv = 0;
        if (!sample_rail_mv(hal, &mv)) {
            deny(out, OTA_DENY_SENSOR_FAIL);
            return;
        }
        out->has_idle      = true;
        out->v_idle_mv     = mv;
        out->v_forecast_mv = mv;
        out->verdict       = OTA_ALLOW_AC_POWERED;
        return;
    }

    /* 2. Температурний коридор. На морозі опір комірки росте в рази,
       на спеці стирання Flash виходить за паспортний діапазон. */
    int16_t temp_c = 0;
    if (!hal->read_temperature_c(hal->ctx, &temp_c)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    out->has_temp = true;
    out->temp_c   = temp_c;
    if (temp_c < lim->temp_min_c) {
        deny(out, OTA_DENY_COLD);
        return;
    }
    if (temp_c > lim->temp_max_c) {
        deny(out, OTA_DENY_HOT);
        return;
    }

    /* 3. Залишковий заряд за паливоміром — груба, але дешева відсічка. */
    uint8_t soc = 0;
    if (!hal->read_soc_percent(hal->ctx, &soc)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    out->has_soc      = true;
    out->soc_percent  = soc;
    if (soc < lim->min_soc_percent) {
        deny(out, OTA_DENY_LOW_SOC);
        return;
    }

    /* 4. Напруга спокою до вмикання сильнострумових вузлів. */
    uint16_t v_idle = 0;
    if (!sample_rail_mv(hal, &v_idle)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    out->has_idle  = true;
    out->v_idle_mv = v_idle;
    if (v_idle < ota_gate_safe_floor_mv(lim)) {
        deny(out, OTA_DENY_LOW_SOC);
        return;
    }

    /* 5. Зводимо латч і тільки тоді вантажимо комірку. Якщо шина
       провалиться, скид застане нас саме тут — і слід лишиться в NV. */
    latch.armed = true;
    if (!latch_store(hal, &latch)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }

    uint16_t v_load = 0;
    bool pulse_ok = pulse_measure(hal, &v_load);

    latch.armed = false;
    if (!latch_store(hal, &latch)) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    if (!pulse_ok) {
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }
    if (v_load > v_idle) {
        /* Під навантаженням напруга не росте: або дільник, або мультиплексор
           АЦП бреше, і довіряти такому виміру не можна. */
        deny(out, OTA_DENY_SENSOR_FAIL);
        return;
    }

    out->has_pulse = true;
    out->v_load_mv = v_load;

    uint16_t delta_test = (uint16_t)(v_idle - v_load);
    uint32_t esr = ((uint32_t)delta_test * 1000u + lim->test_load_ma / 2u) / lim->test_load_ma;
    out->esr_mohm = (esr > UINT16_MAX) ? UINT16_MAX : (uint16_t)esr;

    /* 6. Прогноз найгіршого просідання під піковим струмом OTA. */
    uint16_t forecast = 0;
    bool have_forecast = forecast_rail_mv(v_idle, delta_test,
                                          lim->test_load_ma, lim->ota_peak_ma,
                                          &forecast);
    out->v_forecast_mv = forecast;
    if (have_forecast && forecast >= ota_gate_safe_floor_mv(lim)) {
        out->verdict = OTA_ALLOW_BATTERY_OK;
        return;
    }

    /* 7. Критичний патч безпеки заслуговує на другу спробу — з утричі
       нижчою частотою ядра, повільнішою шиною Flash і тихішим радіо. */
    if (emergency_security_fix) {
        uint16_t eased = 0;
        if (forecast_rail_mv(v_idle, delta_test,
                             lim->test_load_ma, lim->ota_peak_throttled_ma,
                             &eased)
            && eased >= ota_gate_safe_floor_mv(lim)) {
            out->v_forecast_mv = eased;
            out->throttled     = true;
            out->throttle      = OTA_THROTTLE_SAFE;
            out->verdict       = OTA_ALLOW_THROTTLED;
            return;
        }
    }

    deny(out, OTA_DENY_HIGH_ESR);
}

bool ota_gate_clear_faults(const ota_hal_t *hal)
{
    if (hal == NULL || hal->nv_store == NULL) {
        return false;
    }
    latch_t clean = { .armed = false, .faults = 0 };
    return latch_store(hal, &clean);
}
