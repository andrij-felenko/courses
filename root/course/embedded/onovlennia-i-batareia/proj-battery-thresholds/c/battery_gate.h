#ifndef BATTERY_GATE_H
#define BATTERY_GATE_H

#include <stdbool.h>
#include <stdint.h>

/* Передпольотний шлюз живлення: вирішує, чи можна зараз стирати Flash.
   Усе спілкування з залізом — крізь ota_hal_t, тож автомат перевіряється
   на моделі плати без єдиного справжнього регістра. */

typedef enum {
    OTA_ALLOW_AC_POWERED = 0, /* Дозволено: живить зовнішнє джерело */
    OTA_ALLOW_BATTERY_OK,     /* Дозволено: батарея витримає піковий струм */
    OTA_ALLOW_THROTTLED,      /* Дозволено, але лише в пом'якшеному режимі */
    OTA_DENY_COLD,            /* Заборонено: комірка переохолоджена */
    OTA_DENY_HOT,             /* Заборонено: комірка перегріта */
    OTA_DENY_LOW_SOC,         /* Заборонено: замало заряду */
    OTA_DENY_HIGH_ESR,        /* Заборонено: прогноз просідання пробиває BOR */
    OTA_DENY_POWER_FAULT,     /* Заборонено: попередні спроби гасли по живленню */
    OTA_DENY_SENSOR_FAIL      /* Заборонено: вимірювальні кола не відповідають */
} ota_verdict_t;

/* Пороги допуску. Значення за замовчуванням — в OTA_LIMITS_DEFAULT. */
typedef struct {
    int16_t  temp_min_c;            /* нижній край температурного коридору */
    int16_t  temp_max_c;            /* верхній край */
    uint8_t  min_soc_percent;       /* мінімальний залишковий заряд */
    uint16_t v_bor_mv;              /* апаратний поріг Brownout Reset */
    uint16_t bor_margin_mv;         /* запас над ним: V_bor_safe = BOR + margin */
    uint16_t test_load_ma;          /* струм каліброваного тестового навантаження */
    uint16_t ota_peak_ma;           /* піковий струм під час стирання й радіо */
    uint16_t ota_peak_throttled_ma; /* те саме в пом'якшеному режимі */
    uint8_t  max_power_faults;      /* скільки зривів живлення терпимо */
} ota_limits_t;

/* Пом'якшений режим: чим саме гасимо апетит по струму. */
typedef struct {
    uint8_t cpu_mhz;
    uint8_t spi_mhz;
    int8_t  tx_dbm;
} ota_throttle_t;

/* Драйвери платформи. Усі показники повертаються через out-параметр,
   а false означає «коло не відповідає» — це не те саме, що «нуль». */
typedef struct {
    bool (*vbus_present)(void *ctx);
    bool (*read_temperature_c)(void *ctx, int16_t *out_temp_c);
    bool (*read_soc_percent)(void *ctx, uint8_t *out_soc);
    bool (*read_voltage_mv)(void *ctx, uint16_t *out_mv);
    void (*set_test_load)(void *ctx, bool on);
    void (*delay_ms)(void *ctx, uint32_t ms);
    void (*delay_us)(void *ctx, uint32_t us);
    bool (*nv_load)(void *ctx, uint32_t *out_word);  /* backup-регістр RTC */
    bool (*nv_store)(void *ctx, uint32_t word);      /* переживає скид ядра */
    void *ctx;
} ota_hal_t;

/* Усе, що шлюз намиряв дорогою. Порожні поля позначені прапорцями has_*,
   бо «0 °C» і «не міряли» — різні речі, і в телеметрії теж. */
typedef struct {
    ota_verdict_t  verdict;
    bool           throttled;
    ota_throttle_t throttle;
    bool           has_temp;
    bool           has_soc;
    bool           has_idle;
    bool           has_pulse;
    int16_t        temp_c;
    uint8_t        soc_percent;
    uint16_t       v_idle_mv;
    uint16_t       v_load_mv;
    uint16_t       v_forecast_mv;
    uint16_t       esr_mohm;      /* повний послідовний опір: комірка + монтаж */
    uint8_t        power_faults;
} ota_gate_report_t;

extern const ota_limits_t   OTA_LIMITS_DEFAULT;
extern const ota_throttle_t OTA_THROTTLE_SAFE;

/* Головний прохід автомата. out заповнюється завжди, навіть на відмові. */
void ota_gate_evaluate(const ota_hal_t *hal,
                       const ota_limits_t *lim,
                       bool emergency_security_fix,
                       ota_gate_report_t *out);

/* Скинути лічильник зривів живлення — після успішно прошитого образу. */
bool ota_gate_clear_faults(const ota_hal_t *hal);

bool        ota_gate_allowed(const ota_gate_report_t *report);
uint16_t    ota_gate_safe_floor_mv(const ota_limits_t *lim);
const char *ota_verdict_name(ota_verdict_t verdict);

#endif /* BATTERY_GATE_H */
