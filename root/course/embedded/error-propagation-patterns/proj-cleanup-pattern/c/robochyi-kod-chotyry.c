#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include <stdlib.h>

static const char *TAG = "logger";

esp_err_t logger_open(logger_t *lg)
{
    // (1) ВСІ ресурси — оголосити й ОБНУЛИТИ. Це і робить cleanup безпечним:
    //     незахоплене лишиться нульовим, і його звільнення стане пустишкою.
    esp_err_t        ret  = ESP_OK;          // (2) локальний код для всіх гілок
    spi_port_t      *port = NULL;
    uint8_t         *buf  = NULL;
    sd_file_t       *file = NULL;
    SemaphoreHandle_t mtx = NULL;

    // (3) Захоплення по черзі; кожен крок — сторож, що при невдачі стрибає вниз.

    port = spi_port_open(SPI2_HOST);
    if (port == NULL) {                       // порт зайнятий або не налаштований
        ret = ESP_ERR_NOT_FOUND;
        ESP_LOGE(TAG, "spi_port_open failed");
        goto cleanup;                         // нічого ще не взято — cleanup пройде вхолосту
    }

    buf = malloc(SECTOR_SIZE);
    if (buf == NULL) {                        // купа вичерпана
        ret = ESP_ERR_NO_MEM;
        ESP_LOGE(TAG, "malloc(%d) failed", SECTOR_SIZE);
        goto cleanup;                         // звільнить лише port; buf і далі NULL
    }

    file = sd_fopen(port, "/log.bin");        // файл — ПОВЕРХ відкритого порту
    if (file == NULL) {
        ret = ESP_ERR_NOT_FOUND;
        ESP_LOGE(TAG, "sd_fopen failed");
        goto cleanup;                         // звільнить buf і port; file ще NULL
    }

    mtx = xSemaphoreCreateMutex();            // м'ютекс — боронить уже наявний файл
    if (mtx == NULL) {                        // нема пам'яті під об'єкт м'ютекса
        ret = ESP_ERR_NO_MEM;
        ESP_LOGE(TAG, "xSemaphoreCreateMutex failed");
        goto cleanup;                         // звільнить file, buf, port
    }

    // Дійшли сюди — усе захоплено. Віддаємо назовні й виходимо ЩАСЛИВО,
    // але через ТУ САМУ мітку: ret лишився ESP_OK, тож звільнення не буде.
    lg->port = port;
    lg->buf  = buf;
    lg->file = file;
    lg->mtx  = mtx;
    return ESP_OK;                            // власник переданий — НЕ чіпаємо cleanup

cleanup:
    // (4) Звільнення у ЗВОРОТНОМУ до захоплення порядку. Кожне безпечне для NULL,
    //     тож хоч на якому кроці впали — пройдемо всі, звільнимо лише взяте.
    if (mtx)  vSemaphoreDelete(mtx);          // останній узятий — перший звільнений
    if (file) sd_fclose(file);                // файл — раніше за порт, на якому він сидить
    free(buf);                                // free(NULL) безпечний — перевірка зайва
    if (port) spi_port_close(port);           // порт — в останню чергу, основа всього
    return ret;                               // (5) єдиний код помилки нагору
}
