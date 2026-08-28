#include "esp_heap_caps.h"

// великий рідко-чіпаний кадр — у PSRAM:
uint16_t *fb  = heap_caps_malloc(320 * 240 * 2, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

// маленький гарячий буфер, критичний за часом — у внутрішній SRAM:
uint8_t  *hot = heap_caps_malloc(2 * 1024,      MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);

if (!fb || !hot) { /* чесна обробка браку, не мовчазне «якось працюватиме» */ }
// звільняють обидва звичайним free()
