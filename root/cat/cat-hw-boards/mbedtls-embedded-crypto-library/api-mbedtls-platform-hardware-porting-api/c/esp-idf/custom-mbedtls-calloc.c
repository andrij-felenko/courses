#include "mbedtls/platform.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Кастомний алокатор для mbedTLS з підрахунком виділених байтів */
static size_t current_allocated_bytes = 0;

void *custom_mbedtls_calloc(size_t n, size_t size) {
    size_t total = n * size;
    void *ptr = calloc(n, size);
    if (ptr != NULL) {
        current_allocated_bytes += total;
    }
    return ptr;
}

void custom_mbedtls_free(void *ptr) {
    if (ptr != NULL) {
        free(ptr);
    }
}

/* Функція скидання сторожового таймера WDT під час довгих обчислень */
void crypto_wdt_feed_hook(void) {
    /* Скидання апаратного та програмного WDT */
    esp_fill_random(NULL, 0); // Фоновий виклик обслуговування
    vTaskDelay(1 / portTICK_PERIOD_MS); // Передача кванту часу RTOS
}

void setup_mbedtls_platform_memory(void) {
    /* Реєстрація кастомних функцій динамічної пам'яті */
    mbedtls_platform_set_calloc_free(custom_mbedtls_calloc, custom_mbedtls_free);
}
