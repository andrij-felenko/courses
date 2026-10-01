#include "dt838_analyzer.h"
#include <stddef.h>

dt838_diode_result_t dt838_analyze_diode(float raw_voltage_mv) {
    dt838_diode_result_t result;
    result.voltage_drop_mv = raw_voltage_mv;

    if (raw_voltage_mv < 0.0f) {
        result.type = DIODE_TYPE_UNKNOWN;
        result.description = "Некоректна від'ємна напруга";
    } else if (raw_voltage_mv < DT838_DIODE_SHORT_MV) {
        result.type = DIODE_TYPE_SHORT_CIRCUIT;
        result.description = "Коротке замикання (пробій p-n переходу)";
    } else if (raw_voltage_mv >= DT838_DIODE_GE_MIN_MV && raw_voltage_mv <= DT838_DIODE_GE_MAX_MV) {
        result.type = DIODE_TYPE_GERMANIUM;
        result.description = "Германієвий діод або діод Шотткі";
    } else if (raw_voltage_mv >= DT838_DIODE_SI_MIN_MV && raw_voltage_mv <= DT838_DIODE_SI_MAX_MV) {
        result.type = DIODE_TYPE_SILICON;
        result.description = "Кремнієвий діод або p-n перехід BJT";
    } else if (raw_voltage_mv >= DT838_DIODE_LED_MIN_MV && raw_voltage_mv <= DT838_DIODE_LED_MAX_MV) {
        result.type = DIODE_TYPE_LED;
        result.description = "Світлодіод (LED)";
    } else if (raw_voltage_mv >= DT838_DIODE_OPEN_MV) {
        result.type = DIODE_TYPE_OPEN_CIRCUIT;
        result.description = "Обрив кола / зворотний напрямок (індикація 1)";
    } else {
        result.type = DIODE_TYPE_UNKNOWN;
        result.description = "Нетипове значення спаду напруги";
    }

    return result;
}

dt838_continuity_result_t dt838_analyze_continuity(float raw_resistance_ohm) {
    dt838_continuity_result_t result;
    result.resistance_ohm = raw_resistance_ohm;

    if (raw_resistance_ohm < 0.0f) {
        result.state = CONTINUITY_OPEN;
        result.beeper_active = false;
    } else if (raw_resistance_ohm <= DT838_CONTINUITY_BEEP_OHM) {
        result.state = CONTINUITY_CLOSED_BEEP;
        result.beeper_active = true;
    } else if (raw_resistance_ohm < 2000000.0f) {
        result.state = CONTINUITY_RESISTIVE;
        result.beeper_active = false;
    } else {
        result.state = CONTINUITY_OPEN;
        result.beeper_active = false;
    }

    return result;
}

dt838_hfe_result_t dt838_calculate_hfe(float measured_ic_ua) {
    dt838_hfe_result_t result;
    result.collector_current_ua = measured_ic_ua;

    if (measured_ic_ua < 0.0f) {
        result.hfe_gain = 0.0f;
        result.valid = false;
        return result;
    }

    /* Обчислення коефіцієнта підсилення hFE = Ic / Ib */
    result.hfe_gain = measured_ic_ua / DT838_TRANSISTOR_IB_UA;

    /* Перевірка допустимого діапазону шкали DT-838 (0..1000) */
    if (result.hfe_gain <= 1000.0f) {
        result.valid = true;
    } else {
        result.valid = false;
    }

    return result;
}
