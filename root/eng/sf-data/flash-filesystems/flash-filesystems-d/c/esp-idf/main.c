#include <stdio.h>
#include "esp_littlefs.h"
#include "esp_log.h"

static const char *TAG = "log";

void app_main(void) {
    // Змонтувати розділ "storage" у точку /littlefs; форматувати, якщо тому ще немає.
    esp_vfs_littlefs_conf_t conf = {
        .base_path = "/littlefs",
        .partition_label = "storage",
        .format_if_mount_failed = true,
        .dont_mount = false,
    };
    esp_err_t err = esp_vfs_littlefs_register(&conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "LittleFS: монтування не вдалося (%s)", esp_err_to_name(err));
        return;
    }

    // "a" — відкрити на ДОПИСУВАННЯ: новий текст лягає в кінець,
    // старі рядки лишаються недоторкані (на відміну від "w", що затирає).
    FILE *f = fopen("/littlefs/log.txt", "a");
    if (f == NULL) { ESP_LOGE(TAG, "не відкрити log.txt на запис"); return; }
    fprintf(f, "08:01  старт\n");
    fprintf(f, "08:05  кнопка\n");
    fclose(f);                       // тільки після fclose() дані напевно на Flash

    // Прочитати весь файл від початку до кінця.
    f = fopen("/littlefs/log.txt", "r");
    if (f != NULL) {
        char line[64];
        while (fgets(line, sizeof(line), f) != NULL) ESP_LOGI(TAG, "%s", line);
        fclose(f);
    }
}
