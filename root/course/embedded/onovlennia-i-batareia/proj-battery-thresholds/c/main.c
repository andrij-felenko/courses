#include <stdint.h>
#include <stdbool.h>

/* Результати оцінки стану живлення для OTA */
typedef enum {
    OTA_BATTERY_ALLOW_AC_POWERED = 0, /* Дозволено: підключено зовнішнє джерело */
    OTA_BATTERY_ALLOW_BATTERY_OK = 1, /* Дозволено: параметри акумулятора в нормі */
    OTA_BATTERY_DENY_COLD        = 2, /* Заборонено: температура надто низька */
    OTA_BATTERY_DENY_HOT         = 3, /* Заборонено: температура надто висока */
    OTA_BATTERY_DENY_LOW_SOC     = 4, /* Заборонено: недостатній рівень заряду */
    OTA_BATTERY_DENY_HIGH_ESR    = 5, /* Заборонено: високе просідання під навантаженням */
    OTA_BATTERY_DENY_SENSOR_FAIL = 6  /* Заборонено: апаратний збій вимірювальних кіл */
} ota_battery_verdict_t;

/* Структура конфігурації безпекових порогів */
typedef struct {
    int16_t  temp_min_c;          /* Мінімальна температура (+5 °C) */
    int16_t  temp_max_c;          /* Максимальна температура (+45 °C) */
    uint8_t  min_soc_percent;     /* Мінімальний SoC (45 %) */
    uint16_t v_bor_safe_mv;       /* Поріг відсікання безпеки BOR (2900 мВ) */
    uint16_t test_load_current_ma;/* Струм тестового навантаження (200 мА) */
    uint16_t ota_peak_current_ma; /* Максимальний піковий струм OTA (320 мА) */
} ota_battery_limits_t;

/* Інтерфейс драйверів апаратної платформи */
typedef struct {
    bool     (*is_vbus_present)(void);
    bool     (*read_temperature_c)(int16_t *out_temp_c);
    bool     (*read_soc_percent)(uint8_t *out_soc);
    uint16_t (*read_voltage_mv)(void);
    void     (*set_test_load)(bool enable);
    void     (*delay_ms)(uint32_t ms);
} ota_platform_hal_t;

/* Головний автомат перевірки допуску */
ota_battery_verdict_t ota_battery_evaluate_safety(
    const ota_platform_hal_t *hal,
    const ota_battery_limits_t *limits,
    uint16_t *out_forecast_mv
) {
    if (!hal || !limits) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }

    /* 1. Перевірка зовнішнього живлення: якщо USB/мережа активна — безумовний пуск */
    if (hal->is_vbus_present && hal->is_vbus_present()) {
        if (out_forecast_mv) {
            *out_forecast_mv = hal->read_voltage_mv();
        }
        return OTA_BATTERY_ALLOW_AC_POWERED;
    }

    /* 2. Валідація температури комірки */
    int16_t temp_c = 0;
    if (!hal->read_temperature_c || !hal->read_temperature_c(&temp_c)) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }
    if (temp_c < limits->temp_min_c) {
        return OTA_BATTERY_DENY_COLD;
    }
    if (temp_c > limits->temp_max_c) {
        return OTA_BATTERY_DENY_HOT;
    }

    /* 3. Валідація стану заряду (SoC) */
    uint8_t soc = 0;
    if (!hal->read_soc_percent || !hal->read_soc_percent(&soc)) {
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }
    if (soc < limits->min_soc_percent) {
        return OTA_BATTERY_DENY_LOW_SOC;
    }

    /* 4. Активний імпульсний стрес-тест просідання напруги */
    uint16_t v_idle_mv = hal->read_voltage_mv();
    if (v_idle_mv < limits->v_bor_safe_mv) {
        return OTA_BATTERY_DENY_LOW_SOC;
    }

    /* Вмикаємо каліброване тестове навантаження на 15 мс */
    hal->set_test_load(true);
    hal->delay_ms(15);
    uint16_t v_load_mv = hal->read_voltage_mv();
    hal->set_test_load(false);

    /* Обов'язкова пауза релаксації після тестового імпульсу */
    hal->delay_ms(50);

    if (v_load_mv > v_idle_mv) {
        /* Аномалія вимірювання напруги */
        return OTA_BATTERY_DENY_SENSOR_FAIL;
    }

    uint16_t delta_v_test_mv = v_idle_mv - v_load_mv;

    /* Розрахунок прогнозованого просідання під піковим струмом OTA:
       Delta_V_ota = Delta_V_test * (I_ota_peak / I_test) */
    uint32_t delta_v_ota_mv = ((uint32_t)delta_v_test_mv * limits->ota_peak_current_ma) 
                            / limits->test_load_current_ma;

    if (delta_v_ota_mv >= v_idle_mv) {
        return OTA_BATTERY_DENY_HIGH_ESR;
    }

    uint16_t v_forecast_mv = (uint16_t)(v_idle_mv - delta_v_ota_mv);

    if (out_forecast_mv) {
        *out_forecast_mv = v_forecast_mv;
    }

    /* Перевірка, чи не пробиває прогнозована напруга поріг BOR */
    if (v_forecast_mv < limits->v_bor_safe_mv) {
        return OTA_BATTERY_DENY_HIGH_ESR;
    }

    return OTA_BATTERY_ALLOW_BATTERY_OK;
}
