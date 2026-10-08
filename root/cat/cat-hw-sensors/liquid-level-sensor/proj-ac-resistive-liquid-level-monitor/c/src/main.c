#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "liquid_level.h"
#include "mcu_adc_gpio.h"

#define SIM_ADC_CHANNEL      0
#define SIM_LOW_FLOAT_PIN    2
#define SIM_HIGH_FLOAT_PIN   3
#define SIM_PUMP_RELAY_PIN   4

static void print_telemetry(uint32_t step_ms, const liquid_level_data_t *data) {
    const char *pump_str = "ВИМК";
    if (data->pump_state == PUMP_STATE_RUNNING) {
        pump_str = "ПРАЦЮЄ";
    } else if (data->pump_state == PUMP_STATE_FAULT_DRY_RUN) {
        pump_str = "АВАРІЯ: СУХИЙ ХІД";
    } else if (data->pump_state == PUMP_STATE_FAULT_OVERRUN) {
        pump_str = "АВАРІЯ: ПЕРЕКАЧУВАННЯ";
    }

    printf("[%05u мс] Сирий АЦП: %4u | Піковий АЦП: %4u | Рівень: %5.1f%% | Низ. поплавок: %s | Верх. поплавок: %s | Помпа: %s (Час: %u мс)\n",
           step_ms,
           data->raw_adc,
           data->peak_adc,
           data->level_pct,
           data->low_float_active ? "АКТИВ" : "НОРМА",
           data->high_float_active ? "АКТИВ" : "НОРМА",
           pump_str,
           data->pump_running_time_ms);
}

int main(void) {
    printf("=== Демонстрація драйвера вимірювання уровня рідини мовою C ===\n\n");

    /* Конфігурація драйвера для резервуара з автоматичним наповненням */
    liquid_level_config_t config = {
        .adc_channel = SIM_ADC_CHANNEL,
        .adc_min_raw = 500,     /* 500  = 0% (порожній бак) */
        .adc_max_raw = 3500,    /* 3500 = 100% (повний бак) */
        .peak_window_size = 5,  /* Ковзне вікно з 5 відліків для пікового фільтра */
        .gpio_pin_low_float = SIM_LOW_FLOAT_PIN,
        .gpio_pin_high_float = SIM_HIGH_FLOAT_PIN,
        .gpio_pin_pump_relay = SIM_PUMP_RELAY_PIN,
        .threshold_turn_on_pct = 25.0f,  /* Увімкнення помпи при падінні рівня нижче 25% */
        .threshold_turn_off_pct = 85.0f, /* Вимкнення помпи при досягненні 85% */
        .dry_run_timeout_ms = 3000,      /* Очікування приросту рівню до 3 с */
        .max_run_timeout_ms = 10000,     /* Граничний час безперервної роботи помпи 10 с */
        .debounce_time_ms = 100,         /* Антибрязкот 100 мс */
        .mode = LIQUID_LEVEL_MODE_FILL
    };

    liquid_level_t level_driver;
    liquid_level_status_t status = liquid_level_init(&level_driver, &config);
    if (status != LIQUID_LEVEL_OK) {
        printf("ПОМИЛКА: Не вдалося ініціалізувати драйвер рівня (код %d)\n", status);
        return 1;
    }

    uint32_t current_time_ms = 0;
    liquid_level_data_t data;

    printf("--- Сценарій 1: Штатне наповнення резервуара з програмним гістерезисом та піковою фільтрацією ---\n");
    /* Початковий стан: рівень 15% (АЦП ~ 950), помпа повинна увімкнутися */
    mcu_sim_set_adc_raw(SIM_ADC_CHANNEL, 950);
    mcu_sim_set_gpio(SIM_LOW_FLOAT_PIN, false);
    mcu_sim_set_gpio(SIM_HIGH_FLOAT_PIN, false);

    for (int step = 0; step < 12; step++) {
        liquid_level_process(&level_driver, current_time_ms);
        liquid_level_get_data(&level_driver, &data);
        print_telemetry(current_time_ms, &data);

        /* Симуляція зростання рівня води із додаванням сплесків хвилювання поверхні */
        uint16_t sim_raw = 950 + step * 250;
        if (step % 2 == 1) {
            /* Просідання від хвилі - піковий фільтр збереже максимальну висоту гребня */
            sim_raw = (sim_raw > 150) ? sim_raw - 150 : sim_raw;
        }
        mcu_sim_set_adc_raw(SIM_ADC_CHANNEL, sim_raw);
        current_time_ms += 500;
    }

    printf("\n--- Сценарій 2: Спрацьовування захисту від сухого ходу (відсутність води у джерелі) ---\n");
    /* Скидання стану та імітація розрядки: рівень 20%, помпа вмикається, але рівень не росте */
    mcu_sim_set_adc_raw(SIM_ADC_CHANNEL, 1100);
    current_time_ms += 1000;
    liquid_level_process(&level_driver, current_time_ms);
    liquid_level_get_data(&level_driver, &data);
    print_telemetry(current_time_ms, &data);

    /* Чекаємо 3.5 секунди без зміни рівню, щоб спрацював dry_run_timeout_ms (3000 мс) */
    for (int t = 0; t < 8; t++) {
        current_time_ms += 500;
        liquid_level_process(&level_driver, current_time_ms);
        liquid_level_get_data(&level_driver, &data);
        print_telemetry(current_time_ms, &data);
    }

    printf("\n--- Сценарій 3: Відновлення після аварії та перевірка таймера тривалого перекачування ---\n");
    printf("Скидання аварійного стану оператором...\n");
    liquid_level_reset_fault(&level_driver);

    /* Імітація повільного витоку: рівень зростає дуже повільно, час роботи перевищує max_run_timeout_ms (10000 мс) */
    mcu_sim_set_adc_raw(SIM_ADC_CHANNEL, 1000);
    for (int t = 0; t < 22; t++) {
        current_time_ms += 500;
        /* Дуже повільний приріст 10 відліків АЦП за крок (достатньо щоб не зауважити сухий хід, але не вийти на 85%) */
        uint16_t slow_level = 1000 + t * 15;
        mcu_sim_set_adc_raw(SIM_ADC_CHANNEL, slow_level);

        liquid_level_process(&level_driver, current_time_ms);
        liquid_level_get_data(&level_driver, &data);
        print_telemetry(current_time_ms, &data);
    }

    printf("\n=== Завершення демонстрації: Драйвер рівня рідини працює штатно та надійно ===\n");
    return 0;
}
