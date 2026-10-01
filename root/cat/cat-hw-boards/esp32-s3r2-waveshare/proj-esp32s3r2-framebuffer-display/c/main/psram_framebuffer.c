#include "psram_framebuffer.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "PSRAM_FB";

// Зворотний виклик (callback) по завершенню асинхронного DMA-копіювання
static bool dma_async_memcpy_cb(async_memcpy_handle_t mcp_hdl, async_memcpy_event_t *event, void *cb_args)
{
    psram_fb_t *fb = (psram_fb_t *)cb_args;
    fb->swap_pending = false;
    return false;
}

esp_err_t psram_fb_init(psram_fb_t *fb, uint16_t width, uint16_t height)
{
    if (fb == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    fb->size = width * height * FB_BYTES_PER_PIXEL;
    fb->swap_pending = false;

    // Виділяємо пам'ять під два буфери у зовнішній SPIRAM (PSRAM) з вирівнюванням під вимоги DMA/Кешу
    fb->buffer_a = (uint8_t *)heap_caps_aligned_alloc(64, fb->size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    fb->buffer_b = (uint8_t *)heap_caps_aligned_alloc(64, fb->size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

    if (fb->buffer_a == NULL || fb->buffer_b == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити %d байт у PSRAM для кадрових буферів", fb->size);
        psram_fb_deinit(fb);
        return ESP_ERR_NO_MEM;
    }

    // Початкове обнулення кадрових буферів
    memset(fb->buffer_a, 0, fb->size);
    memset(fb->buffer_b, 0, fb->size);

    // Встановлюємо початкові вказівники активного та фонового буферів
    fb->front_buffer = fb->buffer_a;
    fb->back_buffer = fb->buffer_b;

    // Конфігурація драйвера асинхронного копіювання даних через DMA
    async_memcpy_config_t async_memcpy_config = ASYNC_MEMCPY_DEFAULT_CONFIG();
    async_memcpy_config.backlog = 8;

    esp_err_t ret = esp_async_memcpy_install(&async_memcpy_config, &fb->async_memcpy);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації апарату DMA async memcpy: %s", esp_err_to_name(ret));
        psram_fb_deinit(fb);
        return ret;
    }

    ESP_LOGI(TAG, "Подвійний буфер у PSRAM успішно створено. Розмір кадру: %d байт", fb->size);
    return ESP_OK;
}

esp_err_t psram_fb_flush_cache(psram_fb_t *fb)
{
    if (fb == NULL || fb->back_buffer == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    // Примусове очищення й синхронізація L1/L2 кешу ЦПУ з зовнішньою пам'яттю PSRAM,
    // щоб контролер DMA зчитав актуально згенеровані пікселі.
    esp_err_t ret = esp_cache_msync((void *)fb->back_buffer, fb->size, ESP_CACHE_MSYNC_FLAG_DIR_C2M);
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Скидання кешу завершилося з попередженням: %s", esp_err_to_name(ret));
    }
    return ret;
}

void psram_fb_swap(psram_fb_t *fb)
{
    if (fb == NULL) {
        return;
    }

    // Атомарне перемикання вказівників буферів (double buffering)
    uint8_t *temp = fb->front_buffer;
    fb->front_buffer = fb->back_buffer;
    fb->back_buffer = temp;

    fb->swap_pending = true;

    // Запуск асинхронної DMA-передачі для оновлення кадру без блокування ЦПУ
    esp_async_memcpy(fb->async_memcpy, (void *)fb->front_buffer, (void *)fb->back_buffer, fb->size, dma_async_memcpy_cb, fb);
}

void psram_fb_deinit(psram_fb_t *fb)
{
    if (fb == NULL) {
        return;
    }

    if (fb->async_memcpy != NULL) {
        esp_async_memcpy_uninstall(fb->async_memcpy);
        fb->async_memcpy = NULL;
    }

    if (fb->buffer_a != NULL) {
        heap_caps_free(fb->buffer_a);
        fb->buffer_a = NULL;
    }

    if (fb->buffer_b != NULL) {
        heap_caps_free(fb->buffer_b);
        fb->buffer_b = NULL;
    }

    fb->front_buffer = NULL;
    fb->back_buffer = NULL;
}
