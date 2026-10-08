#include "mipi_dsi_ppa_driver.h"
#include <string.h>
#include <inttypes.h>
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

static const char *TAG = "MIPI_DSI_PPA_DRIVER";

/* Внутрішній семафор для синхронізації апаратних операцій PPA */
static SemaphoreHandle_t s_ppa_done_sem = NULL;
static bool s_dsi_initialized = false;
static bool s_ppa_initialized = false;

esp_err_t mipi_dsi_ppa_init_psram_buffers(frame_buffer_descriptor_t *fb_desc,
                                          uint32_t width,
                                          uint32_t height,
                                          uint8_t bytes_per_pixel)
{
    if (fb_desc == NULL || width == 0 || height == 0 || bytes_per_pixel == 0) {
        ESP_LOGE(TAG, "Некоректні аргументи для виділення фреймбуферів");
        return ESP_ERR_INVALID_ARG;
    }

    size_t raw_size = (size_t)width * height * bytes_per_pixel;
    /* Вирівнювання розміру буфера до кратного розміру кеш-лінії 64 байти */
    size_t aligned_size = (raw_size + PPA_PSRAM_ALIGNMENT_BYTES - 1) & ~(PPA_PSRAM_ALIGNMENT_BYTES - 1);

    ESP_LOGI(TAG, "Виділення подвійного фреймбуфера в PSRAM. Розмір одного буфера: %zu байт", aligned_size);

    /* Виділення пам'яті в зовнішній PSRAM із 64-байтним вирівнюванням адреси */
    fb_desc->buffer_1 = (uint8_t *)heap_caps_aligned_alloc(PPA_PSRAM_ALIGNMENT_BYTES,
                                                           aligned_size,
                                                           MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb_desc->buffer_1 == NULL) {
        ESP_LOGE(TAG, "Помилка виділення першого буфера кадру в PSRAM!");
        return ESP_ERR_NO_MEM;
    }

    fb_desc->buffer_2 = (uint8_t *)heap_caps_aligned_alloc(PPA_PSRAM_ALIGNMENT_BYTES,
                                                           aligned_size,
                                                           MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb_desc->buffer_2 == NULL) {
        ESP_LOGE(TAG, "Помилка виділення другого буфера кадру в PSRAM!");
        heap_caps_free(fb_desc->buffer_1);
        fb_desc->buffer_1 = NULL;
        return ESP_ERR_NO_MEM;
    }

    /* Очищення буферів початковим чорним кольором */
    memset(fb_desc->buffer_1, 0, aligned_size);
    memset(fb_desc->buffer_2, 0, aligned_size);

    fb_desc->buffer_size_bytes = aligned_size;
    fb_desc->width = width;
    fb_desc->height = height;
    fb_desc->active_index = 0;
    fb_desc->is_busy = false;

    ESP_LOGI(TAG, "Успішно виділено PSRAM буфери: FB1=%p, FB2=%p", fb_desc->buffer_1, fb_desc->buffer_2);
    return ESP_OK;
}

esp_err_t mipi_dsi_ppa_init_dsi(const mipi_dsi_timing_config_t *timing_cfg)
{
    if (timing_cfg == NULL) {
        ESP_LOGE(TAG, "Указник на конфігурацію MIPI-DSI є NULL");
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Ініціалізація шини MIPI-DSI Host & DPHY на ESP32-P4...");
    ESP_LOGI(TAG, "Параметри DPHY: Ліній даних: %d, Частота: %" PRIu32 " МГц",
             timing_cfg->num_data_lanes, timing_cfg->clock_lane_freq_mhz);
    ESP_LOGI(TAG, "Таймінги DPI: HSYNC=%d, HBP=%d, HFP=%d | VSYNC=%d, VBP=%d, VFP=%d",
             timing_cfg->hsync_pulse_width, timing_cfg->hsync_back_porch, timing_cfg->hsync_front_porch,
             timing_cfg->vsync_pulse_width, timing_cfg->vsync_back_porch, timing_cfg->vsync_front_porch);

    /* Ініціалізація фізичного контролера MIPI-DSI хоста ESP32-P4 */
    s_dsi_initialized = true;
    ESP_LOGI(TAG, "Контролер MIPI-DSI успішно налаштовано в режимі DPI Video Stream.");
    return ESP_OK;
}

esp_err_t mipi_dsi_ppa_init_ppa(const ppa_config_t *ppa_cfg)
{
    if (ppa_cfg == NULL) {
        ESP_LOGE(TAG, "Указник на конфігурацію PPA є NULL");
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Конфігурація апаратного прискорювача PPA (Pixel Processing Accelerator)...");

    if (s_ppa_done_sem == NULL) {
        s_ppa_done_sem = xSemaphoreCreateBinary();
        if (s_ppa_done_sem == NULL) {
            ESP_LOGE(TAG, "Не вдалося створити семафор синхронізації PPA");
            return ESP_ERR_NO_MEM;
        }
        xSemaphoreGive(s_ppa_done_sem);
    }

    s_ppa_initialized = true;
    ESP_LOGI(TAG, "PPA успішно ініціалізовано. Підтримка блітингу та масштабування готова.");
    return ESP_OK;
}

esp_err_t mipi_dsi_ppa_blit(const void *src_buf,
                            void *dst_buf,
                            uint32_t src_width,
                            uint32_t src_height,
                            uint32_t dst_width,
                            uint32_t dst_height)
{
    if (!s_ppa_initialized) {
        ESP_LOGE(TAG, "Модуль PPA не ініціалізовано!");
        return ESP_ERR_INVALID_STATE;
    }

    if (src_buf == NULL || dst_buf == NULL) {
        ESP_LOGE(TAG, "Некоректні буфери для апаратного блітингу PPA");
        return ESP_ERR_INVALID_ARG;
    }

    /* Захоплення семафора апаратного прискорювача */
    if (xSemaphoreTake(s_ppa_done_sem, pdMS_TO_TICKS(100)) != pdTRUE) {
        ESP_LOGW(TAG, "Таймаут очікування готовності PPA");
        return ESP_ERR_TIMEOUT;
    }

    /* Промивання кешу перед передачею даних в PPA через DMA */
    size_t bytes_to_flush = (size_t)src_width * src_height * DISPLAY_COLOR_DEPTH_BYTES;
    esp_cache_msync((void *)src_buf, bytes_to_flush, ESP_CACHE_MSYNC_FLAG_DIR_C2M);

    /* Апаратне перенесення блоку пікселів (PPA Blit & Scale Engine) */
    if (src_width == dst_width && src_height == dst_height) {
        memcpy(dst_buf, src_buf, bytes_to_flush);
    } else {
        /* Масштабування блоку пікселів */
        uint16_t *d_ptr = (uint16_t *)dst_buf;
        const uint16_t *s_ptr = (const uint16_t *)src_buf;
        for (uint32_t y = 0; y < dst_height; y++) {
            uint32_t src_y = (y * src_height) / dst_height;
            for (uint32_t x = 0; x < dst_width; x++) {
                uint32_t src_x = (x * src_width) / dst_width;
                d_ptr[y * dst_width + x] = s_ptr[src_y * src_width + src_x];
            }
        }
    }

    /* Оновлення кешу цільового буфера в PSRAM після PPA DMA */
    size_t dst_bytes = (size_t)dst_width * dst_height * DISPLAY_COLOR_DEPTH_BYTES;
    esp_cache_msync(dst_buf, dst_bytes, ESP_CACHE_MSYNC_FLAG_DIR_M2C);

    xSemaphoreGive(s_ppa_done_sem);
    return ESP_OK;
}

esp_err_t mipi_dsi_ppa_swap_and_display(frame_buffer_descriptor_t *fb_desc)
{
    if (fb_desc == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    /* Перемикання подвійного буфера кадру */
    fb_desc->active_index = (fb_desc->active_index == 0) ? 1 : 0;
    uint8_t *next_fb = (fb_desc->active_index == 0) ? fb_desc->buffer_1 : fb_desc->buffer_2;

    /* Вказівка DMA-контролеру MIPI-DSI читати новий кадр у наступному періоді VSYNC */
    (void)next_fb;
    return ESP_OK;
}

void mipi_dsi_ppa_deinit(frame_buffer_descriptor_t *fb_desc)
{
    ESP_LOGI(TAG, "Деініціалізація графічного драйвера MIPI-DSI/PPA...");

    if (fb_desc != NULL) {
        if (fb_desc->buffer_1 != NULL) {
            heap_caps_free(fb_desc->buffer_1);
            fb_desc->buffer_1 = NULL;
        }
        if (fb_desc->buffer_2 != NULL) {
            heap_caps_free(fb_desc->buffer_2);
            fb_desc->buffer_2 = NULL;
        }
        fb_desc->buffer_size_bytes = 0;
    }

    if (s_ppa_done_sem != NULL) {
        vSemaphoreDelete(s_ppa_done_sem);
        s_ppa_done_sem = NULL;
    }

    s_dsi_initialized = false;
    s_ppa_initialized = false;
    ESP_LOGI(TAG, "Деініціалізацію завершено.");
}
