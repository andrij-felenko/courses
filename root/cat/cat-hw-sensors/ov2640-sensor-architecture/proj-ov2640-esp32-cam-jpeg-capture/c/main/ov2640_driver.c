#include "ov2640_driver.h"
#include "ov2640_regs.h"
#include "sccb.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include <string.h>

static const char *TAG = "ov2640_driver";

#define MAX_JPEG_FRAME_SIZE (512 * 1024)  /* 512 КБ максимальний розмір JPEG кадру у PSRAM */

static ov2640_config_t s_config;
static bool s_driver_initialized = false;
static QueueHandle_t s_fb_queue = NULL;
static QueueHandle_t s_fb_reuse_queue = NULL;
static camera_fb_t *s_fb_pool = NULL;
static uint8_t **s_fb_buffers = NULL;

static esp_err_t enable_xclk(int pin, uint32_t freq_hz) {
    ESP_LOGI(TAG, "Налаштування генератора XCLK на GPIO%d (частота %lu Гц) через LEDC", pin, (unsigned long)freq_hz);
    ledc_timer_config_t timer_conf = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_1_BIT,
        .freq_hz         = freq_hz,
        .clk_cfg         = LEDC_AUTO_CLK
    };
    esp_err_t err = ledc_timer_config(&timer_conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації таймера LEDC: 0x%x", err);
        return err;
    }

    ledc_channel_config_t ch_conf = {
        .gpio_num   = pin,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 1,
        .hpoint     = 0
    };
    err = ledc_channel_config(&ch_conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації каналу LEDC: 0x%x", err);
        return err;
    }
    return ESP_OK;
}

static void disable_xclk(void) {
    ledc_stop(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
}

static esp_err_t write_reg_list(const ov2640_reg_val_t *list) {
    while (list->reg != 0xFF || list->val != 0xFF) {
        if (list->reg == OV2640_BANK_SEL) {
            esp_err_t err = sccb_set_bank(OV2640_SCCB_ADDR, list->val);
            if (err != ESP_OK) return err;
        } else {
            esp_err_t err = sccb_write_reg(OV2640_SCCB_ADDR, list->reg, list->val);
            if (err != ESP_OK) return err;
        }
        list++;
    }
    return ESP_OK;
}

esp_err_t ov2640_check_id(uint16_t *pid_mid) {
    uint8_t pid = 0, ver = 0;
    esp_err_t err = sccb_set_bank(OV2640_SCCB_ADDR, BANK_SENSOR);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося переключити банк на BANK_SENSOR");
        return err;
    }

    err = sccb_read_reg(OV2640_SCCB_ADDR, OV2640_REG_PID, &pid);
    if (err != ESP_OK) return err;

    err = sccb_read_reg(OV2640_SCCB_ADDR, OV2640_REG_VER, &ver);
    if (err != ESP_OK) return err;

    uint16_t id = ((uint16_t)pid << 8) | ver;
    if (pid_mid) {
        *pid_mid = id;
    }

    ESP_LOGI(TAG, "Зчитано ідентифікатор сенсора OV2640: 0x%04X (PID: 0x%02X, VER: 0x%02X)", id, pid, ver);
    if (pid != 0x26 || ver != 0x42) {
        ESP_LOGE(TAG, "Некоректний ідентифікатор сенсора! Очікується 0x2640");
        return ESP_ERR_NOT_FOUND;
    }
    return ESP_OK;
}

esp_err_t ov2640_reset(void) {
    ESP_LOGI(TAG, "Скидання регістрів OV2640...");
    if (s_config.pin_reset >= 0) {
        gpio_set_level(s_config.pin_reset, 0);
        vTaskDelay(pdMS_TO_TICKS(10));
        gpio_set_level(s_config.pin_reset, 1);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    return write_reg_list(ov2640_reset_regs);
}

esp_err_t ov2640_set_framesize(framesize_t size) {
    s_config.frame_size = size;
    const ov2640_reg_val_t *regs = NULL;
    switch (size) {
        case FRAMESIZE_CIF:  regs = ov2640_cif_jpeg_regs; break;
        case FRAMESIZE_SVGA: regs = ov2640_svga_jpeg_regs; break;
        case FRAMESIZE_UXGA: regs = ov2640_uxga_jpeg_regs; break;
        default: regs = ov2640_svga_jpeg_regs; break;
    }
    return write_reg_list(regs);
}

esp_err_t ov2640_set_quality(uint8_t quality) {
    if (quality < 1) quality = 1;
    if (quality > 63) quality = 63;
    s_config.jpeg_quality = quality;

    esp_err_t err = sccb_set_bank(OV2640_SCCB_ADDR, BANK_DSP);
    if (err != ESP_OK) return err;

    return sccb_write_reg(OV2640_SCCB_ADDR, OV2640_REG_QS, quality);
}

static void dma_capture_task(void *pvParameters) {
    (void)pvParameters;
    size_t width = 800;
    size_t height = 600;

    while (s_driver_initialized) {
        camera_fb_t *fb = NULL;
        if (xQueueReceive(s_fb_reuse_queue, &fb, pdMS_TO_TICKS(100)) == pdTRUE) {
            switch (s_config.frame_size) {
                case FRAMESIZE_CIF:  width = 352;  height = 288;  break;
                case FRAMESIZE_SVGA: width = 800;  height = 600;  break;
                case FRAMESIZE_UXGA: width = 1600; height = 1200; break;
            }

            /* Імітація вивантаження кадру з DMA та визначення межі JPEG (SOI 0xFFD8 / EOI 0xFFD9) */
            fb->buf[0] = 0xFF; fb->buf[1] = 0xD8; /* JPEG Start of Image */
            fb->buf[2] = 0xFF; fb->buf[3] = 0xE0;
            fb->buf[4] = 0x00; fb->buf[5] = 0x10;
            fb->buf[6] = 'J';  fb->buf[7] = 'F';  fb->buf[8] = 'I'; fb->buf[9] = 'F';
            fb->buf[10] = 0x00;

            size_t dummy_payload_len = 32768;
            memset(fb->buf + 11, 0xAA, dummy_payload_len);

            size_t eoi_idx = 11 + dummy_payload_len;
            fb->buf[eoi_idx] = 0xFF;
            fb->buf[eoi_idx + 1] = 0xD9; /* JPEG End of Image */

            fb->len = eoi_idx + 2;
            fb->width = width;
            fb->height = height;
            fb->format = s_config.pix_format;
            fb->timestamp = esp_timer_get_time();

            if (xQueueSend(s_fb_queue, &fb, pdMS_TO_TICKS(50)) != pdTRUE) {
                /* У разі переповнення повертаємо буфер назад */
                xQueueSend(s_fb_reuse_queue, &fb, 0);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(33)); /* ~30 FPS */
    }
    vTaskDelete(NULL);
}

esp_err_t ov2640_init(const ov2640_config_t *config) {
    if (!config) return ESP_ERR_INVALID_ARG;
    if (s_driver_initialized) return ESP_OK;

    memcpy(&s_config, config, sizeof(ov2640_config_t));

    /* Налаштування GPIO для PWDN та RESET */
    if (s_config.pin_pwdn >= 0) {
        gpio_config_t io_conf = {
            .pin_bit_mask = (1ULL << s_config.pin_pwdn),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE
        };
        gpio_config(&io_conf);
        gpio_set_level(s_config.pin_pwdn, 0); /* Активація сенсора */
    }

    if (s_config.pin_reset >= 0) {
        gpio_config_t io_conf = {
            .pin_bit_mask = (1ULL << s_config.pin_reset),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE
        };
        gpio_config(&io_conf);
        gpio_set_level(s_config.pin_reset, 1);
    }

    /* Запуск тактування XCLK */
    esp_err_t err = enable_xclk(s_config.pin_xclk, s_config.xclk_freq_hz);
    if (err != ESP_OK) return err;

    vTaskDelay(pdMS_TO_TICKS(10));

    /* Ініціалізація шини SCCB */
    err = sccb_init(s_config.pin_sscb_sda, s_config.pin_sscb_scl, 100000);
    if (err != ESP_OK) {
        disable_xclk();
        return err;
    }

    /* Перевірка ID пристрою OV2640 */
    uint16_t pid_mid = 0;
    err = ov2640_check_id(&pid_mid);
    if (err != ESP_OK) {
        sccb_deinit();
        disable_xclk();
        return err;
    }

    /* Скидання та вивантаження базової конфігурації регістрів */
    ov2640_reset();
    vTaskDelay(pdMS_TO_TICKS(20));

    ESP_LOGI(TAG, "Вивантаження послідовності ініціалізації Sensor та DSP...");
    err = write_reg_list(ov2640_sensor_init_regs);
    if (err != ESP_OK) return err;

    err = write_reg_list(ov2640_dsp_init_regs);
    if (err != ESP_OK) return err;

    err = write_reg_list(ov2640_jpeg_init_regs);
    if (err != ESP_OK) return err;

    err = ov2640_set_framesize(s_config.frame_size);
    if (err != ESP_OK) return err;

    err = ov2640_set_quality(s_config.jpeg_quality);
    if (err != ESP_OK) return err;

    /* Виділення кадрових буферів у PSRAM */
    size_t count = (s_config.fb_count > 0) ? s_config.fb_count : 1;
    s_fb_pool = (camera_fb_t *)calloc(count, sizeof(camera_fb_t));
    s_fb_buffers = (uint8_t **)calloc(count, sizeof(uint8_t *));
    if (!s_fb_pool || !s_fb_buffers) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять під метадані кадрових буферів");
        return ESP_ERR_NO_MEM;
    }

    s_fb_queue = xQueueCreate(count, sizeof(camera_fb_t *));
    s_fb_reuse_queue = xQueueCreate(count, sizeof(camera_fb_t *));

    for (size_t i = 0; i < count; i++) {
        s_fb_buffers[i] = (uint8_t *)heap_caps_malloc(MAX_JPEG_FRAME_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (!s_fb_buffers[i]) {
            ESP_LOGE(TAG, "Помилка виділення %d байт у PSRAM для буфера DMA #%u", MAX_JPEG_FRAME_SIZE, (unsigned int)i);
            return ESP_ERR_NO_MEM;
        }
        s_fb_pool[i].buf = s_fb_buffers[i];
        camera_fb_t *p_fb = &s_fb_pool[i];
        xQueueSend(s_fb_reuse_queue, &p_fb, 0);
    }

    s_driver_initialized = true;
    xTaskCreate(dma_capture_task, "dma_capture", 4096, NULL, 10, NULL);

    ESP_LOGI(TAG, "Драйвер камери OV2640 успішно ініціалізовано (%u буферів DMA у PSRAM)", (unsigned int)count);
    return ESP_OK;
}

esp_err_t ov2640_deinit(void) {
    if (!s_driver_initialized) return ESP_OK;

    s_driver_initialized = false;
    vTaskDelay(pdMS_TO_TICKS(100));

    sccb_deinit();
    disable_xclk();

    if (s_fb_buffers) {
        for (size_t i = 0; i < s_config.fb_count; i++) {
            if (s_fb_buffers[i]) {
                heap_caps_free(s_fb_buffers[i]);
            }
        }
        free(s_fb_buffers);
        s_fb_buffers = NULL;
    }

    if (s_fb_pool) {
        free(s_fb_pool);
        s_fb_pool = NULL;
    }

    if (s_fb_queue) {
        vQueueDelete(s_fb_queue);
        s_fb_queue = NULL;
    }

    if (s_fb_reuse_queue) {
        vQueueDelete(s_fb_reuse_queue);
        s_fb_reuse_queue = NULL;
    }

    ESP_LOGI(TAG, "Драйвер камери деініціалізовано");
    return ESP_OK;
}

camera_fb_t* ov2640_get_frame(uint32_t timeout_ms) {
    if (!s_driver_initialized || !s_fb_queue) return NULL;
    camera_fb_t *fb = NULL;
    if (xQueueReceive(s_fb_queue, &fb, pdMS_TO_TICKS(timeout_ms)) == pdTRUE) {
        return fb;
    }
    return NULL;
}

void ov2640_return_frame(camera_fb_t *fb) {
    if (!fb || !s_fb_reuse_queue) return;
    xQueueSend(s_fb_reuse_queue, &fb, 0);
}
