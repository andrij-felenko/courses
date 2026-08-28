#include "esp_ota_ops.h"

esp_err_t do_ota_update(void) {
    // 1. Обрати ВІЛЬНИЙ слот (не той, з якого виконуємось)
    const esp_partition_t *target = esp_ota_get_next_update_partition(NULL);
    if (target == NULL) return ESP_FAIL;          // нема куди писати

    // 2. Почати OTA: це СТИРАЄ цільовий слот і дає робочий «дескриптор»
    esp_ota_handle_t handle = 0;
    esp_err_t err = esp_ota_begin(target, OTA_SIZE_UNKNOWN, &handle);
    if (err != ESP_OK) return err;

    // 3. Приймати образ ШМАТКАМИ й одразу писати у Flash.
    //    Буфер крихітний — увесь образ у RAM не тримаємо.
    uint8_t buf[1024];
    int n;
    while ((n = receive_next_chunk(buf, sizeof(buf))) > 0) {  // n=0 → образ скінчився
        err = esp_ota_write(handle, buf, n);
        if (err != ESP_OK) {
            esp_ota_abort(handle);                // збій запису → відкинути, слот робочий цілий
            return err;
        }
    }

    // 4. Завершити: тут IDF ПЕРЕВІРЯЄ образ (цілість, а з secure boot — і ПІДПИС)
    err = esp_ota_end(handle);                    // образ битий або непідписаний → помилка
    if (err != ESP_OK) return err;

    // 5. Атомарно перемкнути завантаження на новий слот (робочий слот досі цілий!)
    err = esp_ota_set_boot_partition(target);
    if (err != ESP_OK) return err;

    // 6. Перезавантажитись у новий образ — у ПРОБНИЙ запуск
    esp_restart();
    return ESP_OK;                               // сюди вже не дійдемо
}
