#include "esp_heap_caps.h"
#include <stdint.h>
#include <stddef.h>

#define FB_W 320
#define FB_H 240
#define FB_BYTES (FB_W * FB_H * 2)   // 2 байти/піксель → 153 600 байтів (150 КіБ)

uint16_t *framebuffer_alloc(void) {
    // MALLOC_CAP_SPIRAM — «дай саме із зовнішньої PSRAM».
    // 8BIT — блок придатний для побайтового доступу (звичайні дані).
    uint16_t *fb = heap_caps_malloc(FB_BYTES, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (fb == NULL) {
        // PSRAM не ввімкнена в конфігурації або в ній забракло місця —
        // мовчазний відкат у внутрішню SRAM лише замаскує проблему,
        // тож тут чесніше повідомити про брак пам'яті.
        return NULL;
    }
    return fb;                         // далі — звичайний покажчик, ніякого SPI у коді
}
