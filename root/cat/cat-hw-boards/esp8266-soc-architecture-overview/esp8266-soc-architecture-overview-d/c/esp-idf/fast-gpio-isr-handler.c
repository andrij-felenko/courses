#include "esp_system.h"
#include "esp_log.h"
#include "osapi.h"

static const char *TAG = "MEM_MONITOR";

// Розміщення критичного обробника у пам'яті IRAM для забезпечення нульової затримки
void ICACHE_RAM_ATTR fast_gpio_isr_handler(void *arg) {
    // Внутрішній обробник переривання виконується напряму з IRAM
    uint32_t gpio_status = GPIO_REG_READ(GPIO_STATUS_ADDRESS);
    GPIO_REG_WRITE(GPIO_STATUS_W1TC_ADDRESS, gpio_status);
}

void print_memory_telemetry(void) {
    uint32_t free_heap = system_get_free_heap_size();
    
    // Вивід поточного стану оперативної пам'яті DRAM
    os_printf("[%s] Доступна купа Heap: %u байтів\n", TAG, free_heap);
    
    if (free_heap < 10240) {
        os_printf("[%s] ПОПЕРЕДЖЕННЯ: Залишок Heap критично малий! Ризик OOM.\n", TAG);
    }
}
