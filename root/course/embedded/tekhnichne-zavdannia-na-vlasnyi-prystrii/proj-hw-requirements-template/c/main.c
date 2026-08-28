#include <stdio.h>
#include <stdbool.h>

/* Структура параметрів циклу споживання */
typedef struct {
    float i_sleep_ua;       /* Струм сну (мкА) */
    float t_sleep_s;        /* Тривалість сну (секунди) */
    float i_sense_ma;       /* Струм фази вимірювань (мА) */
    float t_sense_ms;       /* Тривалість вимірювань (мілісекунди) */
    float i_tx_ma;          /* Струм передачі радіо (мА) */
    float t_tx_ms;          /* Тривалість передачі (мілісекунди) */
    float bat_capacity_mah; /* Номінальна ємність батареї (мА·год) */
    float self_discharge_pct_year; /* Річний саморозряд батареї (%) */
    float safety_margin_pct;       /* Інженерний запас на старіння (%) */
} power_spec_t;

/* Результат розрахунку енергетичного балансу */
typedef struct {
    float i_avg_ua;         /* Середньозважений струм (мкА) */
    float battery_life_years; /* Розрахунковий час автономної роботи (роки) */
    bool meets_target;      /* Чи досягнуто цільову автономність */
} power_result_t;

/* Обчислення енергетичного бюджету та терміну служби */
power_result_t evaluate_power_budget(const power_spec_t *spec, float target_years) {
    power_result_t res = {0};
    if (!spec || target_years <= 0.0f) return res;

    /* Переведення часів у секунди */
    float t_sense_s = spec->t_sense_ms / 1000.0f;
    float t_tx_s = spec->t_tx_ms / 1000.0f;
    float t_cycle_s = spec->t_sleep_s + t_sense_s + t_tx_s;

    if (t_cycle_s <= 0.0f) return res;

    /* Сумарний заряд за цикл у міліампер-секундах (мА·с) */
    float q_sleep = (spec->i_sleep_ua / 1000.0f) * spec->t_sleep_s;
    float q_sense = spec->i_sense_ma * t_sense_s;
    float q_tx    = spec->i_tx_ma * t_tx_s;
    float q_total_mas = q_sleep + q_sense + q_tx;

    /* Середній струм у мікроамперах (мкА) */
    res.i_avg_ua = (q_total_mas / t_cycle_s) * 1000.0f;

    /* Ефективна ємність з урахуванням запасу */
    float usable_capacity = spec->bat_capacity_mah * (1.0f - spec->safety_margin_pct / 100.0f);

    /* Щорічне споживання пристрою (мА·год/рік) */
    float annual_consumption = (res.i_avg_ua / 1000.0f) * 8760.0f;

    /* Щорічні втрати від саморозряду */
    float annual_self_discharge = spec->bat_capacity_mah * (spec->self_discharge_pct_year / 100.0f);

    /* Повний річний розхід енергії */
    float annual_total_drain = annual_consumption + annual_self_discharge;

    if (annual_total_drain > 0.0f) {
        res.battery_life_years = usable_capacity / annual_total_drain;
    }

    res.meets_target = (res.battery_life_years >= target_years);
    return res;
}

int main(void) {
    power_spec_t itn01_spec = {
        .i_sleep_ua = 15.0f,
        .t_sleep_s = 299.85f,
        .i_sense_ma = 12.0f,
        .t_sense_ms = 100.0f,
        .i_tx_ma = 120.0f,
        .t_tx_ms = 50.0f,
        .bat_capacity_mah = 8500.0f,      /* Елемент ER26500 */
        .self_discharge_pct_year = 1.5f,   /* LiSOCl2 хімія */
        .safety_margin_pct = 15.0f         /* 15% запас на холод */
    };

    power_result_t result = evaluate_power_budget(&itn01_spec, 5.0f);

    printf("--- Результати оцінки ТЗ (Power Budget) ---\n");
    printf("Середній струм (I_avg): %.2f мкА\n", result.i_avg_ua);
    printf("Час автономної роботи:  %.2f років\n", result.battery_life_years);
    printf("Відповідність вимозі:   %s\n", result.meets_target ? "ПРОЙДЕНО (PASS)" : "НЕ ПРОЙДЕНО (FAIL)");

    return 0;
}
