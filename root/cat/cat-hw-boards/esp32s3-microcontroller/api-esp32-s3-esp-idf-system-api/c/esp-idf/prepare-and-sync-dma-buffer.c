#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "esp_log.h"

static const char *TAG = "cache_dma";

esp_err_t prepare_and_sync_dma_buffer(size_t buffer_size)
{
    // Виділення пам'яті в PSRAM з вирівнюванням за межею кеш-лінії (32 байти)
    size_t alignment = 32;
    uint8_t *tx_buffer = (uint8_t *)heap_caps_aligned_alloc(alignment, buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
    if (!tx_buffer) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM");
        return ESP_ERR_NO_MEM;
    }

    // Заповнення буфера новими даними від ЦП
    memset(tx_buffer, 0xAA, buffer_size);

    // Скидання брудних кеш-ліній у PSRAM перед стартом DMA-передачі
    esp_err_t err = esp_cache_msync(tx_buffer, buffer_size, ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка синхронізації кешу: %s", esp_err_to_name(err));
        heap_caps_free(tx_buffer);
        return err;
    }

    // Запуск DMA-передачі (наприклад, на периферійний модуль LCD або SPI)
    // start_dma_transfer(tx_buffer, buffer_size);

    return ESP_OK;
}
