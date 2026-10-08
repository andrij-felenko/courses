#include "camera_driver.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "sensor.h"

static const char *TAG = "CAMERA_DRIVER";

esp_err_t camera_driver_init(void)
{
    /* Перевірка наявності та функціонування зовнішьої PSRAM пам'яті */
    if (!esp_psram_is_initialized()) {
        ESP_LOGE(TAG, "Зовнішню пам'ять PSRAM не виявлено! Відеобуфери камери вимагають PSRAM через Octal SPI.");
        return ESP_ERR_NOT_FOUND;
    }

    ESP_LOGI(TAG, "PSRAM ініціалізовано. Розмір доступної PSRAM: %d байт", (int)esp_psram_get_size());

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

        .xclk_freq_hz = CAM_XCLK_FREQ_HZ,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_VGA,

        .jpeg_quality = 12,
        .fb_count = 2,
        .fb_location = CAMERA_FB_IN_PSRAM,
        .grab_mode = CAMERA_GRAB_LATEST
    };

    /* Ініціалізація драйвера esp_camera */
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери: 0x%x (%s)", err, esp_err_to_name(err));
        return err;
    }

    /* Налаштування параметрів сенсора зображення */
    sensor_t *s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_vflip(s, 1);       /* Дзеркальне відображення по вертикалі */
        s->set_hmirror(s, 0);     /* Нормальне відображення по горизонталі */
        s->set_brightness(s, 0);  /* Базовий рівень яскравості */
        s->set_contrast(s, 0);    /* Базовий рівень контрастності */
    }

    ESP_LOGI(TAG, "Драйвер DVP-камери успішно ініціалізовано з двобуферною схемою в PSRAM.");
    return ESP_OK;
}

esp_camera_fb_t* camera_driver_capture_frame(void)
{
    esp_camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося отримати кадр з сенсора камери");
        return NULL;
    }
    return fb;
}

void camera_driver_return_frame(esp_camera_fb_t *fb)
{
    if (fb) {
        esp_camera_fb_return(fb);
    }
}

esp_err_t camera_driver_deinit(void)
{
    esp_err_t err = esp_camera_deinit();
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Драйвер камери деініціалізовано.");
    } else {
        ESP_LOGE(TAG, "Помилка під час деініціалізації камери: %s", esp_err_to_name(err));
    }
    return err;
}
