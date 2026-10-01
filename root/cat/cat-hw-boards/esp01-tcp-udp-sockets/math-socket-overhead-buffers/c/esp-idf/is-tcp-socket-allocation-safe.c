// Обчислення доступності пам'яті DRAM перед створенням нових сокетів lwIP
#include "esp_system.h"
#include <stdbool.h>

#define TCP_SOCKET_RAM_BYTES 6044
#define SAFETY_DRAM_MARGIN   4096

bool is_tcp_socket_allocation_safe(void) {
    uint32_t free_heap = esp_get_free_heap_size();
    if (free_heap < (TCP_SOCKET_RAM_BYTES + SAFETY_DRAM_MARGIN)) {
        // Недостатньо вільної пам'яті DRAM — відмова від створення сокета для запобігання OOM
        return false;
    }
    return true;
}
