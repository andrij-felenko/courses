#include "esp_camera.h"
#include "human_face_detect_msr01.hpp"
#include "esp_heap_caps.h"

// Резервування арени тензорів у зовнішній PSRAM пам'яті
#define TENSOR_ARENA_SIZE (1024 * 1024)

void init_inference_pipeline(void) {
    uint8_t *tensor_arena = (uint8_t *)heap_caps_malloc(
        TENSOR_ARENA_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT
    );
    if (!tensor_arena) {
        // Обробка помилки нестачі пам'яті в PSRAM
        return;
    }

    // Завантаження квантованої INT8 моделі детекції людей
    HumanFaceDetectMSR01 detector(0.3f, 0.5f, 10, true);
    camera_fb_t *fb = esp_camera_fb_get();

    if (fb) {
        // Виконання прискореного інференсу через векторний прискорювач Xtensa LX7
        auto results = detector.detect((uint8_t *)fb->buf, {fb->height, fb->width, 3});
        esp_camera_fb_return(fb);
    }
}
