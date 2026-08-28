#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include <stdlib.h>

static const char *TAG = "logger";

esp_err_t logger_open(logger_t *lg)
{
    esp_err_t        ret  = ESP_OK;          // макроси GOTO вимагають саме цього імені — ret
    spi_port_t      *port = NULL;
    uint8_t         *buf  = NULL;
    sd_file_t       *file = NULL;
    SemaphoreHandle_t mtx = NULL;

    // ESP_GOTO_ON_FALSE(умова, код, мітка, тег, підпис):
    //   умова хибна → лог + ret = код + goto мітка.
    port = spi_port_open(SPI2_HOST);
    ESP_GOTO_ON_FALSE(port, ESP_ERR_NOT_FOUND, cleanup, TAG, "spi_port_open");

    buf = malloc(SECTOR_SIZE);
    ESP_GOTO_ON_FALSE(buf, ESP_ERR_NO_MEM, cleanup, TAG, "malloc %d", SECTOR_SIZE);

    file = sd_fopen(port, "/log.bin");
    ESP_GOTO_ON_FALSE(file, ESP_ERR_NOT_FOUND, cleanup, TAG, "sd_fopen");

    mtx = xSemaphoreCreateMutex();
    ESP_GOTO_ON_FALSE(mtx, ESP_ERR_NO_MEM, cleanup, TAG, "create mutex");

    lg->port = port; lg->buf = buf; lg->file = file; lg->mtx = mtx;
    return ESP_OK;                            // успіх передає власність — повз cleanup

cleanup:
    if (mtx)  vSemaphoreDelete(mtx);
    if (file) sd_fclose(file);
    free(buf);
    if (port) spi_port_close(port);
    return ret;
}
