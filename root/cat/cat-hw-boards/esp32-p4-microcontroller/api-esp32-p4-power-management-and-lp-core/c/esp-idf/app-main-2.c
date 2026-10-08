#include <stdio.h>
#include "esp_log.h"
#include "esp_err.h"
#include "esp_lp_core.h"
#include "lp_core_main.h" // Автоматично згенерований заголовок прошивки LP-Core

static const char *TAG = "HP_LP_CORE_INIT";

void app_main(void)
{
    ESP_LOGI(TAG, "Ініціалізація та завантаження прошивки LP-Core...");

    // Конфігурація параметрів запуску співпроцесора LP-Core
    esp_lp_core_config_t lp_cfg = {
        .wakeup_source = ESP_LP_CORE_WAKEUP_SOURCE_HP_CPU,
        .lp_core_clock_source = LP_CORE_CLK_SRC_DEFAULT,
    };

    // Завантаження бінарного образу прошивки в оперативну пам'ять LP SRAM
    esp_err_t ret = esp_lp_core_load_binary(lp_core_main_bin_start, 
                                            (lp_core_main_bin_end - lp_core_main_bin_start));
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка завантаження бінарного образу LP-Core: %s", esp_err_to_name(ret));
        return;
    }

    // Запуск виконання коду на співпроцесорі LP-Core
    ret = esp_lp_core_run(&lp_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запуску співпроцесора LP-Core: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "Співпроцесор LP-Core успішно запущено в автономному режимі.");
}
