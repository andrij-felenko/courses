#include "nvs.h"

void bump_boot_count(void)
{
    nvs_handle_t h;
    // відкриваємо простір "app" на читання й запис
    nvs_open("app", NVS_READWRITE, &h);

    int32_t n = 0;                              // значення-замовчування на перший запуск
    esp_err_t err = nvs_get_i32(h, "boot_count", &n);
    if (err == ESP_ERR_NVS_NOT_FOUND) {
        n = 0;                                  // ключа ще нема — лічильник стартує з нуля
    }

    n = n + 1;                                  // порахували це ввімкнення
    nvs_set_i32(h, "boot_count", n);            // поки що лише в RAM
    nvs_commit(h);                              // ось тепер n справді у Flash
    nvs_close(h);
}
