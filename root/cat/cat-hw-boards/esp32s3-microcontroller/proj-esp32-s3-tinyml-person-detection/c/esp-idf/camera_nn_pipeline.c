#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_camera.h"
#include "esp_nn.h"

static const char *TAG = "CAMERA_NN_PIPELINE";

#define CAM_PIN_PWDN    -1
#define CAM_PIN_RESET   -1
#define CAM_PIN_XCLK    10
#define CAM_PIN_SIOD    40
#define CAM_PIN_SIOC    39

#define CAM_PIN_D7      48
#define CAM_PIN_D6      11
#define CAM_PIN_D5      12
#define CAM_PIN_D4      14
#define CAM_PIN_D3      16
#define CAM_PIN_D2      18
#define CAM_PIN_D1      17
#define CAM_PIN_D0      15
#define CAM_PIN_VSYNC   38
#define CAM_PIN_HREF    47
#define CAM_PIN_PCLK    13

#define FRAME_QUEUE_SIZE 2
#define INPUT_DIM 32
#define IN_CHANNELS 3
#define OUT_CHANNELS 16

static QueueHandle_t s_frame_queue = NULL;

// Структура кадрового буфера для передачі між задачами
typedef struct {
    camera_fb_t *fb;
    int frame_id;
} frame_packet_t;

// Конфігурація та ініціалізація драйвера esp32-camera
static esp_err_t init_camera(void)
{
    camera_config_t config = {
        .pin_pwdn = CAM_PIN_PWDN,
        .pin_reset = CAM_PIN_RESET,
        .pin_xclk = CAM_PIN_XCLK,
        .pin_siod = CAM_PIN_SIOD,
        .pin_sioc = CAM_PIN_SIOC,

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

        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,

        .pixel_format = PIXFORMAT_RGB565,
        .frame_size = FRAMESIZE_QVGA,

        .jpeg_quality = 12,
        .fb_count = 2,
        .fb_location = CAMERA_FB_IN_PSRAM,
        .grab_mode = CAMERA_GRAB_WHEN_EMPTY
    };

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації драйвера камери: 0x%x", err);
        return err;
    }
    ESP_LOGI(TAG, "Драйвер камери успішно ініціалізовано в PSRAM через DVP/GDMA");
    return ESP_OK;
}

// Задача захоплення кадрів камери на ядрі PRO_CPU (Core 0)
static void camera_capture_task(void *pvParameters)
{
    int frame_counter = 0;
    ESP_LOGI(TAG, "Запущено задачу захоплення кадрів на ядрі %d", xPortGetCoreID());

    while (1) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGW(TAG, "Не вдалося отримати кадр із фотоматриці");
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        frame_packet_t packet = {
            .fb = fb,
            .frame_id = ++frame_counter
        };

        // Передаємо кадр у чергу інференсу без блокування
        if (xQueueSend(s_frame_queue, &packet, pdMS_TO_TICKS(50)) != pdTRUE) {
            ESP_LOGW(TAG, "Черга кадрів переповнена. Відкидаємо кадр #%d", packet.frame_id);
            esp_camera_fb_return(fb);
        }

        vTaskDelay(pdMS_TO_TICKS(30)); // ~30 FPS
    }
}

// Задача обчислення нейромережі з векторизацією PIE на ядрі APP_CPU (Core 1)
static void nn_inference_task(void *pvParameters)
{
    ESP_LOGI(TAG, "Запущено задачу інференсу ESP-NN на ядрі %d", xPortGetCoreID());

    // Виділяємо буфери з суворим 32-бітним вирівнюванням у PSRAM
    size_t in_size = INPUT_DIM * INPUT_DIM * IN_CHANNELS;
    size_t out_size = INPUT_DIM * INPUT_DIM * OUT_CHANNELS;
    size_t filter_size = IN_CHANNELS * OUT_CHANNELS * 3 * 3;

    int8_t *input_data = (int8_t *)heap_caps_malloc(in_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_32BIT);
    int8_t *output_data = (int8_t *)heap_caps_malloc(out_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_32BIT);
    int8_t *filter_weights = (int8_t *)heap_caps_malloc(filter_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_32BIT);
    int32_t *bias = (int32_t *)heap_caps_malloc(OUT_CHANNELS * sizeof(int32_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_32BIT);

    if (!input_data || !output_data || !filter_weights || !bias) {
        ESP_LOGE(TAG, "Критична помилка: виділення PSRAM пам'яті для векторизованих масивів невдале");
        heap_caps_free(input_data);
        heap_caps_free(output_data);
        heap_caps_free(filter_weights);
        heap_caps_free(bias);
        vTaskDelete(NULL);
        return;
    }

    // Заповнення фіктивними вагами та bias для демо 2D-згортки
    memset(filter_weights, 1, filter_size);
    memset(bias, 0, OUT_CHANNELS * sizeof(int32_t));

    frame_packet_t packet;
    esp_nn_conv_s8_data_t conv_params = {
        .in_x = INPUT_DIM,
        .in_y = INPUT_DIM,
        .in_ch = IN_CHANNELS,
        .out_ch = OUT_CHANNELS,
        .filter_x = 3,
        .filter_y = 3,
        .stride_x = 1,
        .stride_y = 1,
        .pad_x = 1,
        .pad_y = 1,
        .activation_min = -128,
        .activation_max = 127,
    };

    while (1) {
        if (xQueueReceive(s_frame_queue, &packet, portMAX_DELAY) == pdTRUE) {
            // Масштабуємо пікселі кадру у формат INT8 для векторного співпроцесора PIE
            size_t copy_bytes = (packet.fb->len < in_size) ? packet.fb->len : in_size;
            for (size_t i = 0; i < copy_bytes; ++i) {
                input_data[i] = (int8_t)((int)packet.fb->buf[i] - 128);
            }

            // Виконання 2D-згортки з використанням 128-бітного SIMD PIE прискорення
            esp_nn_conv_s8(&conv_params, input_data, output_data, filter_weights, bias);

            ESP_LOGI(TAG, "Оброблено кадр #%d (розмір %d байт) через ESP-NN PIE vectorization",
                     packet.frame_id, (int)packet.fb->len);

            // Обов'язкове повернення кадрового буфера в драйвер esp32-camera
            esp_camera_fb_return(packet.fb);
        }
    }

    heap_caps_free(input_data);
    heap_caps_free(output_data);
    heap_caps_free(filter_weights);
    heap_caps_free(bias);
}

void app_main(void)
{
    ESP_LOGI(TAG, "Ініціалізація мультимедійного конвеєра ESP32-S3 Edge AI");

    s_frame_queue = xQueueCreate(FRAME_QUEUE_SIZE, sizeof(frame_packet_t));
    if (!s_frame_queue) {
        ESP_LOGE(TAG, "Не вдалося створити чергу кадрів FreeRTOS");
        return;
    }

    if (init_camera() != ESP_OK) {
        vQueueDelete(s_frame_queue);
        return;
    }

    // Запускаємо задачу захоплення кадрів на ядрі 0 (PRO_CPU)
    xTaskCreatePinnedToCore(
        camera_capture_task,
        "cam_capture_task",
        4096,
        NULL,
        5,
        NULL,
        0
    );

    // Запускаємо задачу векторизованого інференсу на ядрі 1 (APP_CPU)
    xTaskCreatePinnedToCore(
        nn_inference_task,
        "nn_infer_task",
        8192,
        NULL,
        5,
        NULL,
        1
    );
}
