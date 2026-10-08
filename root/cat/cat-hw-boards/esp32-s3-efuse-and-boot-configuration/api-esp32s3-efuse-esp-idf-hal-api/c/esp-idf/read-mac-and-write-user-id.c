#include <stdio.h>
#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

static const char *TAG = "efuse_hal";

esp_err_t read_mac_and_write_user_id(uint32_t user_id) {
    uint8_t mac_buf[6] = {0};

    // Зчитування апаратної MAC-адреси з заздалегідь визначеного поля
    esp_err_t err = esp_efuse_read_field_blob(ESP_EFUSE_MAC_FACTORY, mac_buf, sizeof(mac_buf) * 8);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка читання MAC-адреси з eFuse: %s", esp_err_to_name(err));
        return err;
    }
    ESP_LOGI(TAG, "Заводська MAC-адреса: %02X:%02X:%02X:%02X:%02X:%02X",
             mac_buf[0], mac_buf[1], mac_buf[2], mac_buf[3], mac_buf[4], mac_buf[5]);

    // Ініціалізація транзакційного пакетного запису
    err = esp_efuse_batch_write_begin();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося розпочати транзакцію eFuse: %s", esp_err_to_name(err));
        return err;
    }

    // Підготовка запису 32-бітного значення у поле USER_DATA
    err = esp_efuse_write_field_blob(ESP_EFUSE_USER_DATA, &user_id, 32);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка підготовки даних USER_DATA: %s", esp_err_to_name(err));
        esp_efuse_batch_write_cancel();
        return err;
    }

    // Фізичне випалювання комірок пам'яті eFuse
    err = esp_efuse_batch_write_commit();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка випалювання бітів у eFuse: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Ідентифікатор користувача успішно випалено в eFuse!");
    return ESP_OK;
}
