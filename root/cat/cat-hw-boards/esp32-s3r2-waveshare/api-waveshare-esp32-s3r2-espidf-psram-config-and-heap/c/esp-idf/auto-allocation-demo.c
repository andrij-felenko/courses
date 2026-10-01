#include <stdio.h>
#include <stdlib.h>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "AUTO_MALLOC";

void auto_allocation_demo(void) {
    // Малий блок (4 КБ) лягає у внутрішню SRAM
    void *small_block = malloc(4096);
    // Великий блок (64 КБ) автоматично перенаправляється в PSRAM
    void *large_block = malloc(65536);

    if (small_block && large_block) {
        bool is_large_in_psram = esp_ptr_external_ram(large_block);
        ESP_LOGI(TAG, "Великий блок розміщено у PSRAM: %s", is_large_in_psram ? "Так" : "Ні");
    }

    free(small_block);
    free(large_block);
}
