// Приклад безпечного виділення динамічної пам'яті в C (ESP8266 Non-OS SDK)
#include "c_types.h"
#include "osapi.h"
#include "mem.h"
#include "user_interface.h"

void process_network_data(const uint8_t *data, uint16_t len) {
    // 1. Зчитування поточного залишку Heap
    uint32_t free_heap = system_get_free_heap_size();
    os_printf("Поточна вільна куча: %u байтів\n", free_heap);

    // 2. Перевірка наявності критичного мінімуму пам'яті (наприклад, 8 КБ)
    if (free_heap < 8192) {
        os_printf("ПОМИЛКА: Недостатньо пам'яті для обробки пакета!\n");
        return;
    }

    // 3. Виділення пам'яті
    uint8_t *buffer = (uint8_t *)os_malloc(len);
    if (buffer == NULL) {
        os_printf("ПОМИЛКА: os_malloc повернув NULL!\n");
        return;
    }

    // 4. Безпечна обробка даних
    os_memcpy(buffer, data, len);

    // 5. Обов'язкове звільнення пам'яті після використання
    os_free(buffer);
    buffer = NULL;
}
