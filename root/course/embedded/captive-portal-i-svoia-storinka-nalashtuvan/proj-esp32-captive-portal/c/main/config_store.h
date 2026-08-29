#pragma once

#include <stdbool.h>
#include "esp_err.h"

/* SSID — до 32 октетів, пароль WPA2 — до 63 символів; плюс байт на нуль. */
#define CONFIG_STORE_SSID_MAX 32
#define CONFIG_STORE_PASS_MAX 63

typedef struct {
    char ssid[CONFIG_STORE_SSID_MAX + 1];
    char password[CONFIG_STORE_PASS_MAX + 1];
} portal_credentials_t;

/* Чи лежить у NVS повний, доведений до кінця запис конфігурації. */
bool config_store_is_configured(void);

/* Читає збережені облікові дані. ESP_ERR_NVS_NOT_FOUND — конфігурації немає. */
esp_err_t config_store_load(portal_credentials_t *out);

/*
 * Записує облікові дані транзакційно: спершу знімає ознаку `configured`,
 * потім кладе поля, і лише останнім кроком ставить ознаку назад.
 * Знеструмлення на будь-якому кроці лишає запис без ознаки — а такий
 * при наступному старті не буде прийнято за валідний.
 */
esp_err_t config_store_save(const char *ssid, const char *password);

/* Забуває конфігурацію: пристрій наступного разу підніме портал. */
esp_err_t config_store_erase(void);
