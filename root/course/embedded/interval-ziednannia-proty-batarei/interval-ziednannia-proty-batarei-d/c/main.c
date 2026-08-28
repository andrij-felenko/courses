#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

/* Структура вхідних параметрів з'єднання BLE */
typedef struct {
    uint16_t conn_interval_min_units; /* у кроках по 1.25 мс (6 .. 3200) */
    uint16_t conn_interval_max_units; /* у кроках по 1.25 мс (6 .. 3200) */
    uint16_t slave_latency;           /* кількість пропущених подій (0 .. 499) */
    uint16_t supervision_timeout_units;/* у кроках по 10 мс (10 .. 3200) */
} ble_conn_params_t;

/* Структура параметрів енергетичного профілю апаратури */
typedef struct {
    float q_event_active_uc; /* Заряд активної події передачі, мкКл (мкА*с) */
    float i_sleep_ua;        /* Струм глибокого сну System ON з RTC, мкА */
    float battery_mah;       /* Номінальна ємність батареї, мА*год (наприклад 225 для CR2032) */
    float battery_esr_ohm;   /* Внутрішній опір батареї, Ом */
    float i_peak_ma;         /* Піковий струм радіотракту, мА */
    float c_bulk_uf;         /* Ємність буферного конденсатора на платі, мкФ */
} ble_power_profile_t;

/* Результат моделювання енергоспоживання */
typedef struct {
    bool is_valid_core_spec;
    bool is_valid_apple_ios;
    float conn_interval_max_ms;
    float effective_interval_ms;
    float supervision_timeout_ms;
    float i_avg_ua;
    float lifetime_days;
    float lifetime_years;
    float v_sag_without_cap_v;
    float v_sag_with_cap_v;
} ble_sim_result_t;

/* Функція валідації та математичного розрахунку */
bool ble_simulate_power(const ble_conn_params_t *params,
                        const ble_power_profile_t *profile,
                        ble_sim_result_t *out_result)
{
    if (!params || !profile || !out_result) return false;

    float min_ms = (float)params->conn_interval_min_units * 1.25f;
    float max_ms = (float)params->conn_interval_max_units * 1.25f;
    float timeout_ms = (float)params->supervision_timeout_units * 10.0f;
    uint16_t latency = params->slave_latency;

    out_result->conn_interval_max_ms = max_ms;
    out_result->supervision_timeout_ms = timeout_ms;
    out_result->effective_interval_ms = max_ms * (float)(1 + latency);

    /* 1. Перевірка за стандартом Bluetooth Core Specification */
    bool core_valid = true;
    if (params->conn_interval_min_units < 6 || params->conn_interval_min_units > 3200) core_valid = false;
    if (params->conn_interval_max_units < 6 || params->conn_interval_max_units > 3200) core_valid = false;
    if (params->conn_interval_min_units > params->conn_interval_max_units) core_valid = false;
    if (latency > 499) core_valid = false;
    if (params->supervision_timeout_units < 10 || params->supervision_timeout_units > 3200) core_valid = false;
    
    /* Правило безпеки Core Spec: Timeout > (1 + latency) * max_ms * 2 */
    if (timeout_ms <= out_result->effective_interval_ms * 2.0f) core_valid = false;
    out_result->is_valid_core_spec = core_valid;

    /* 2. Перевірка за правилами Apple Accessory Design Guidelines */
    bool apple_valid = core_valid;
    if (min_ms < 15.0f) apple_valid = false;
    if (max_ms < min_ms + 15.0f) apple_valid = false;
    if (fmodf(max_ms, 15.0f) > 0.001f && fmodf(max_ms, 15.0f) < 14.999f) apple_valid = false;
    if (latency > 30) apple_valid = false;
    if (timeout_ms > 6000.0f) apple_valid = false;
    if (out_result->effective_interval_ms > 2000.0f) apple_valid = false;
    if (timeout_ms < out_result->effective_interval_ms * 3.0f) apple_valid = false;
    out_result->is_valid_apple_ios = apple_valid;

    /* 3. Розрахунок середнього струму споживання */
    float t_eff_sec = out_result->effective_interval_ms / 1000.0f;
    float i_event_contrib_ua = profile->q_event_active_uc / t_eff_sec;
    out_result->i_avg_ua = i_event_contrib_ua + profile->i_sleep_ua;

    /* 4. Саморозряд батареї (1.2% на рік) та термін роботи */
    float i_self_discharge_ua = (profile->battery_mah * 1000.0f * 0.012f) / 8760.0f;
    float total_drain_ua = out_result->i_avg_ua + i_self_discharge_ua;
    float usable_capacity_uah = (profile->battery_mah * 1000.0f) * 0.88f; /* 88% хімічна віддача */

    float lifetime_hours = usable_capacity_uah / total_drain_ua;
    out_result->lifetime_days = lifetime_hours / 24.0f;
    out_result->lifetime_years = out_result->lifetime_days / 365.25f;

    /* 5. Імпульсне просідання напруги на внутрішньому опорі ESR */
    out_result->v_sag_without_cap_v = (profile->i_peak_ma / 1000.0f) * profile->battery_esr_ohm;
    if (profile->c_bulk_uf > 0.1f) {
        out_result->v_sag_with_cap_v = profile->q_event_active_uc / profile->c_bulk_uf;
    } else {
        out_result->v_sag_with_cap_v = out_result->v_sag_without_cap_v;
    }

    return true;
}

int main(void)
{
    /* Тестовий профіль: CR2032, nRF52840, конденсатор 47 мкФ */
    ble_power_profile_t nrf52_cr2032 = {
        .q_event_active_uc = 15.0f,
        .i_sleep_ua = 2.0f,
        .battery_mah = 225.0f,
        .battery_esr_ohm = 40.0f,
        .i_peak_ma = 12.0f,
        .c_bulk_uf = 47.0f
    };

    /* Набір параметрів для порівняння: iOS Ultra-Low-Power */
    ble_conn_params_t ios_ulp = {
        .conn_interval_min_units = 72,  /* 90.0 мс */
        .conn_interval_max_units = 84,  /* 105.0 мс (кратно 15) */
        .slave_latency = 18,            /* Ефективний інтервал: 105 * 19 = 1995 мс */
        .supervision_timeout_units = 600/* 6000 мс (>= 1995 * 3) */
    };

    ble_sim_result_t res;
    if (ble_simulate_power(&ios_ulp, &nrf52_cr2032, &res)) {
        printf("=== Результати симуляції BLE енергоспоживання ===\n");
        printf("Сумісність з BT Core Spec: %s\n", res.is_valid_core_spec ? "ТАК" : "НІ");
        printf("Сумісність з Apple iOS:    %s\n", res.is_valid_apple_ios ? "ТАК" : "НІ");
        printf("Ефективний інтервал зв'язку: %.1f мс\n", res.effective_interval_ms);
        printf("Середній струм споживання:  %.2f мкА\n", res.i_avg_ua);
        printf("Розрахунковий час життя:    %.1f діб (%.2f років)\n", res.lifetime_days, res.lifetime_years);
        printf("Просідання напруги без C_bulk: %.2f В (Критично!)\n", res.v_sag_without_cap_v);
        printf("Просідання напруги з C=47мкФ:  %.2f В (Безпечно)\n", res.v_sag_with_cap_v);
    }
    return 0;
}
