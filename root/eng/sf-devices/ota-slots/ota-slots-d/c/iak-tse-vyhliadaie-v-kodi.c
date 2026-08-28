#include "esp_ota_ops.h"

esp_err_t install_image(const uint8_t *image, size_t len) {
    // 1. Беремо ПАСИВНИЙ слот — ніколи не той, з якого виконуємось зараз.
    const esp_partition_t *slot = esp_ota_get_next_update_partition(NULL);

    // 2. Готуємо слот і пишемо образ (у житті — шматками з мережі).
    esp_ota_handle_t h = 0;
    esp_err_t err = esp_ota_begin(slot, len, &h);   // стирає пасивний слот
    if (err != ESP_OK) return err;
    err = esp_ota_write(h, image, len);             // робочий слот недоторканий
    if (err != ESP_OK) { esp_ota_abort(h); return err; }

    // 3. esp_ota_end перевіряє цілість образу (а при secure boot — і підпис).
    err = esp_ota_end(h);                           // битий образ далі не пройде
    if (err != ESP_OK) return err;

    // 4. Аж ТЕПЕР — атомарний перемикач otadata на новий слот.
    return esp_ota_set_boot_partition(slot);        // стан слота → "новий"
}
