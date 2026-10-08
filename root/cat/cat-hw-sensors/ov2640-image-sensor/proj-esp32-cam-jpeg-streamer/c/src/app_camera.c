#include "app_camera.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "app_camera";
static bool s_camera_initialized = false;

bool app_camera_is_psram_available(void) {
#if CONFIG_SPIRAM
    return esp_psram_is_initialized();
#else
    return false;
#endif
}

esp_err_t app_camera_init(framesize_t frame_size, pixformat_t pixel_format) {
    if (s_camera_initialized) {
        ESP_LOGW(TAG, "Драйвер камери вже ініціалізовано");
        return ESP_OK;
    }

    /* Скидання живлення камери через PWDN якщо вивід призначений */
    if (CAM_PIN_PWDN != -1) {
        gpio_config_t io_conf = {
            .pin_bit_mask = (1ULL << CAM_PIN_PWDN),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE,
        };
        gpio_config(&io_conf);
        gpio_set_level(CAM_PIN_PWDN, 1);
        vTaskDelay(pdMS_TO_TICKS(10));
        gpio_set_level(CAM_PIN_PWDN, 0);
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    camera_config_t config = {
        .pin_pwdn = CAM_PIN_PWDN,
        .pin_reset = CAM_PIN_RESET,
        .pin_xclk = CAM_PIN_XCLK,
        .pin_sccb_sda = CAM_PIN_SIOD,
        .pin_sccb_scl = CAM_PIN_SIOC,

        .pin_d7 = CAM_PIN_D7,
        .pin_d6 = CAM_PIN_D6,
        .pin_d5 = CAM_PIN_D5,
        .pin_d4 = CAM_PIN_D4,
        .pin_d3 = CAM_PIN_D3,
        .pin_d2 = CAM_PIN_D2,
        .pin_d1 = CAM_PIN_D1,
        .pin_d0 = CAM_PIN_D0,

        .pin_vsync = CAM_PIN_VSYNC,
        .pin_href = CAM_PIN_HREF,
        .pin_pclk = CAM_PIN_PCLK,

        .xclk_freq_hz = 20000000, /* 20 МГц опорна частота генератора */
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = pixel_format,
        .frame_size = frame_size,

        .jpeg_quality = 12,
        .fb_count = 1,
        .grab_mode = CAMERA_GRAB_WHEN_EMPTY,
        .fb_location = CAMERA_FB_IN_PSRAM
    };

    /* Перевірка доступності зовнішньої оперативної пам'яті PSRAM */
    if (app_camera_is_psram_available()) {
        ESP_LOGI(TAG, "Виявлено зовнішню пам'ять PSRAM. Активація подвійної буферизації.");
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
        config.fb_location = CAMERA_FB_IN_PSRAM;
    } else {
        ESP_LOGW(TAG, "PSRAM не виявлено! Обмеження конфігурації для внутрішньої SRAM.");
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 15;
        config.fb_count = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    /* Ініціалізація драйвера esp32-camera */
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера камери: 0x%x", err);
        return err;
    }

    /* Налаштування базових параметрів сенсора OV2640 через SCCB */
    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        if (s->id.PID == OV2640_PID) {
            ESP_LOGI(TAG, "Сенсор OV2640 успішно розпізнано");
            s->set_vflip(s, 1);       /* Вертикальний розворот */
            s->set_hmirror(s, 0);     /* Горизонтальне віддзеркалення */
            s->set_brightness(s, 0);  /* Нормальна яскравість (-2..2) */
            s->set_contrast(s, 0);    /* Нормальний контраст (-2..2) */
            s->set_saturation(s, 0);  /* Насиченість кольору (-2..2) */
        } else {
            ESP_LOGW(TAG, "Підключено сенсор з PID=0x%x (очікувався OV2640)", s->id.PID);
        }
    } else {
        ESP_LOGE(TAG, "Не вдалося отримати вказівник на об'єкт сенсора");
        esp_camera_deinit();
        return ESP_FAIL;
    }

    s_camera_initialized = true;
    ESP_LOGI(TAG, "Ініціалізація підсистеми камери успішно завершена");
    return ESP_OK;
}

esp_err_t app_camera_deinit(void) {
    if (!s_camera_initialized) {
        return ESP_OK;
    }
    esp_err_t err = esp_camera_deinit();
    if (err == ESP_OK) {
        s_camera_initialized = false;
        ESP_LOGI(TAG, "Драйвер камери деініціалізовано");
    }
    return err;
}

esp_err_t app_camera_set_quality(int quality) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    return s->set_quality(s, quality) == 0 ? ESP_OK : ESP_FAIL;
}

esp_err_t app_camera_set_framesize(framesize_t frame_size) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    return s->set_framesize(s, frame_size) == 0 ? ESP_OK : ESP_FAIL;
}

esp_err_t app_camera_set_vflip(int enable) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    return s->set_vflip(s, enable) == 0 ? ESP_OK : ESP_FAIL;
}

esp_err_t app_camera_set_hmirror(int enable) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return ESP_ERR_INVALID_STATE;
    }
    return s->set_hmirror(s, enable) == 0 ? ESP_OK : ESP_FAIL;
}
