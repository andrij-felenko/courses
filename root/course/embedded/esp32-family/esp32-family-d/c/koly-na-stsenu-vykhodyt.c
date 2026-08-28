#include "esp_heap_caps.h"

#define W 640
#define H 480
size_t frame_bytes = (size_t)W * H * 2;   // 614 400 байтів ≈ 600 КБ

// у внутрішню SRAM НЕ влізе (там усього ~512 КБ, ще й з дірками) →
// просимо саме зовнішню PSRAM прапорцем MALLOC_CAP_SPIRAM:
uint16_t *frame = heap_caps_malloc(frame_bytes, MALLOC_CAP_SPIRAM);
if (!frame) {                 // PSRAM може бути не розпаяна або вимкнена в конфігу
    ESP_LOGE("cam", "нема PSRAM під кадр");
    return;
}
// ... працюємо з кадром; доступ повільніший за SRAM, зате він узагалі можливий
heap_caps_free(frame);
