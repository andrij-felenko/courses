// battery_monitor.c — Модуль динамічної діагностики батареї (C99)
#include <stdint.h>
#include <stdbool.h>

#define TEST_LOAD_RESISTOR_OHM   68.0f    // Номінал тестового резистора (Ом)
#define VOLTAGE_MIN_SAFE_MV      2800U    // Поріг безпечної напруги (2.8 В)
#define RESISTANCE_MAX_WARN_OHM  15.0f    // Максимально допустимий опір джерела (Ом)

typedef struct {
    uint32_t (*get_adc_voltage_mv)(void);
    void (*set_load_mosfet)(bool state);
    void (*sleep_us)(uint32_t us);
} pwr_hal_t;

typedef enum {
    BATTERY_OK = 0,
    BATTERY_WARN_HIGH_IMPEDANCE,
    BATTERY_ERR_VOLTAGE_SAG,
    BATTERY_ERR_DEPLETED
} battery_health_t;

typedef struct {
    uint32_t ocv_mv;
    uint32_t v_sag_mv;
    float dynamic_esr_ohm;
    battery_health_t health;
} battery_report_t;

battery_health_t battery_evaluate_health(const pwr_hal_t *hal, battery_report_t *report) {
    if (!hal || !report) {
        return BATTERY_ERR_DEPLETED;
    }

    // 1. Зняття напруги розімкненого кола (OCV)
    hal->set_load_mosfet(false);
    hal->sleep_us(1000); // 1 мс пауза для стабілізації
    report->ocv_mv = hal->get_adc_voltage_mv();

    if (report->ocv_mv < VOLTAGE_MIN_SAFE_MV) {
        report->health = BATTERY_ERR_DEPLETED;
        return BATTERY_ERR_DEPLETED;
    }

    // 2. Короткочасне підключення тестового навантаження (5 мс)
    hal->set_load_mosfet(true);
    hal->sleep_us(2000); // Очікування встановлення перехідного процесу
    report->v_sag_mv = hal->get_adc_voltage_mv();
    hal->set_load_mosfet(false);

    // 3. Розрахунок внутрішнього динамічного опору ESR
    // Струм навантаження I = V_sag / R_load
    // Падіння напруги Delta_V = OCV - V_sag
    // ESR = Delta_V / I = (OCV - V_sag) * R_load / V_sag
    if (report->v_sag_mv > 0) {
        float delta_v = (float)(report->ocv_mv - report->v_sag_mv);
        report->dynamic_esr_ohm = (delta_v * TEST_LOAD_RESISTOR_OHM) / (float)report->v_sag_mv;
    } else {
        report->dynamic_esr_ohm = 999.0f;
    }

    // 4. Оцінка стану здоров'я джерела
    if (report->v_sag_mv < VOLTAGE_MIN_SAFE_MV) {
        report->health = BATTERY_ERR_VOLTAGE_SAG;
    } else if (report->dynamic_esr_ohm > RESISTANCE_MAX_WARN_OHM) {
        report->health = BATTERY_WARN_HIGH_IMPEDANCE;
    } else {
        report->health = BATTERY_OK;
    }

    return report->health;
}
