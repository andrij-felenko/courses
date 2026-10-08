#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

static const char *TAG = "lockdown_hal";

esp_err_t apply_final_device_lockdown(void) {
    ESP_LOGW(TAG, "ПОПЕРЕДЖЕННЯ: Запуск процедури остаточної фіксації блоків eFuse!");

    esp_err_t err = esp_efuse_batch_write_begin();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося розпочати пакетний запис: %s", esp_err_to_name(err));
        return err;
    }

    // Випалювання біта вимкнення фізичних виводів JTAG
    err = esp_efuse_write_field_bit(ESP_EFUSE_DIS_PAD_JTAG);
    if (err != ESP_OK) {
        esp_efuse_batch_write_cancel();
        return err;
    }

    // Захист від модифікації блоку користувацьких даних USER_DATA (EFUSE_BLK3)
    err = esp_efuse_set_write_dis_mask(1 << EFUSE_BLK3);
    if (err != ESP_OK) {
        esp_efuse_batch_write_cancel();
        return err;
    }

    // Захист від зчитування блоку ключів EFUSE_BLK4
    err = esp_efuse_set_read_dis_mask(1 << EFUSE_BLK4);
    if (err != ESP_OK) {
        esp_efuse_batch_write_cancel();
        return err;
    }

    // Фізична фіксація змін у кремнії
    err = esp_efuse_batch_write_commit();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка фіксації захисних масок eFuse: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Апаратне блокування пристрою успішно завершено!");
    return ESP_OK;
}
