#include "nvs_flash.h"
#include "nvs.h"

esp_err_t save_wifi_credentials(const char *ssid, const char *pass) {
    nvs_handle_t handle;
    esp_err_t err = nvs_open("wifi_cfg", NVS_READWRITE, &handle);
    if (err != ESP_OK) return err;

    nvs_set_str(handle, "ssid", ssid);
    nvs_set_str(handle, "password", pass);
    nvs_set_u8(handle, "configured", 1);
    
    err = nvs_commit(handle); // Фіксація транзакції у Flash
    nvs_close(handle);
    return err;
}
