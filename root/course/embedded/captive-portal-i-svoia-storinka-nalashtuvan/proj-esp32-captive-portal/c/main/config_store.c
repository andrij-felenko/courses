#include "config_store.h"

#include <string.h>

#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "cfg";

static const char *NVS_NAMESPACE = "wifi_cfg";
static const char *KEY_SSID = "ssid";
static const char *KEY_PASS = "password";
static const char *KEY_CONFIGURED = "configured";

bool config_store_is_configured(void)
{
    nvs_handle_t nvs;
    if (nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs) != ESP_OK) {
        return false;
    }

    uint8_t flag = 0;
    esp_err_t err = nvs_get_u8(nvs, KEY_CONFIGURED, &flag);
    nvs_close(nvs);

    return err == ESP_OK && flag == 1;
}

esp_err_t config_store_load(portal_credentials_t *out)
{
    if (out == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    memset(out, 0, sizeof(*out));

    nvs_handle_t nvs;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &nvs);
    if (err != ESP_OK) {
        return err;
    }

    uint8_t flag = 0;
    err = nvs_get_u8(nvs, KEY_CONFIGURED, &flag);
    if (err != ESP_OK || flag != 1) {
        nvs_close(nvs);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    size_t len = sizeof(out->ssid);
    err = nvs_get_str(nvs, KEY_SSID, out->ssid, &len);
    if (err != ESP_OK) {
        nvs_close(nvs);
        return err;
    }

    len = sizeof(out->password);
    err = nvs_get_str(nvs, KEY_PASS, out->password, &len);
    if (err == ESP_ERR_NVS_NOT_FOUND) {
        /* Відкрита мережа: ключ пароля просто не заводили. */
        out->password[0] = '\0';
        err = ESP_OK;
    }

    nvs_close(nvs);
    return err;
}

esp_err_t config_store_save(const char *ssid, const char *password)
{
    if (ssid == NULL || ssid[0] == '\0' || strlen(ssid) > CONFIG_STORE_SSID_MAX) {
        return ESP_ERR_INVALID_ARG;
    }
    if (password != NULL && strlen(password) > CONFIG_STORE_PASS_MAX) {
        return ESP_ERR_INVALID_ARG;
    }

    nvs_handle_t nvs;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося відкрити простір імен NVS: %s", esp_err_to_name(err));
        return err;
    }

    /*
     * Крок 1. Знімаємо ознаку завершеності й фіксуємо це окремим комітом.
     * З цієї миті будь-яке падіння живлення лишить пристрій у стані
     * «конфігурації немає» — тобто він підніме портал, а не спробує
     * підключитися напівзаписаними даними.
     */
    err = nvs_set_u8(nvs, KEY_CONFIGURED, 0);
    if (err == ESP_OK) {
        err = nvs_commit(nvs);
    }

    /* Крок 2. Кладемо самі поля. */
    if (err == ESP_OK) {
        err = nvs_set_str(nvs, KEY_SSID, ssid);
    }
    if (err == ESP_OK) {
        err = nvs_set_str(nvs, KEY_PASS, password != NULL ? password : "");
    }
    if (err == ESP_OK) {
        err = nvs_commit(nvs);
    }

    /* Крок 3. Ознака завершеності — останньою, окремим комітом. */
    if (err == ESP_OK) {
        err = nvs_set_u8(nvs, KEY_CONFIGURED, 1);
    }
    if (err == ESP_OK) {
        err = nvs_commit(nvs);
    }

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Запис конфігурації обірвався: %s", esp_err_to_name(err));
    } else {
        ESP_LOGI(TAG, "Конфігурацію для мережі \"%s\" збережено", ssid);
    }

    nvs_close(nvs);
    return err;
}

esp_err_t config_store_erase(void)
{
    nvs_handle_t nvs;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &nvs);
    if (err != ESP_OK) {
        return err;
    }

    err = nvs_erase_all(nvs);
    if (err == ESP_OK) {
        err = nvs_commit(nvs);
    }

    nvs_close(nvs);
    return err;
}
