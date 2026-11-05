#include <stdbool.h>
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>

// Структура токена скасування з атомарним прапорцем
typedef struct {
    atomic_bool cancel_requested;
} cancellation_token_t;

// Перевірка стану токена в контрольній точці
inline bool cancellation_is_requested(const cancellation_token_t *token) {
    if (token == NULL) {
        return false;
    }
    return atomic_load_explicit(&token->cancel_requested, memory_order_acquire);
}

// Робочий цикл обробки даних із кооперативним скасуванням
int process_data_payload(const cancellation_token_t *token, uint8_t *buffer, size_t len) {
    int result_status = 0;

    for (size_t i = 0; i < len; ++i) {
        // Контрольна точка перевірки сигналу зупинки
        if (cancellation_is_requested(token)) {
            result_status = -1; // Статус скасування (CANCELLED)
            goto cleanup;
        }
        
        // Виконання атомарного кроку обробки даних
        buffer[i] = (uint8_t)(buffer[i] ^ 0xAA);
    }

    return result_status;

cleanup:
    // Виконання санітарного очищення апаратних ресурсів і буферів
    hardware_dma_abort();
    hardware_peripheral_reset();
    return result_status;
}
