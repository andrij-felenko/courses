#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Оголошення застарілої функції з атрибутом компілятора */
#if defined(__GNUC__) || defined(__clang__)
#define DEPRECATED(msg) __attribute__((deprecated(msg)))
#elif defined(_MSC_VER)
#define DEPRECATED(msg) __declspec(deprecated(msg))
#else
#define DEPRECATED(msg)
#endif

/* Стара функція: приймає сирий тайм-аут у мілісекундах (буде видалена у v4.0.0) */
DEPRECATED("telemetry_send() застаріла з v3.2.0; використовуйте telemetry_send_fd() з прапорцями якості")
bool telemetry_send(uint32_t msg_id, const uint8_t *payload, size_t len) {
    printf("[WARN-DEPRECATION] Виклик застарілої telemetry_send(id=0x%X). "
           "Оновіть клієнтський код відповідно до Release Notes v3.2.0!\n", msg_id);
    /* Емуляція відправки старого формату */
    return len <= 8;
}

/* Нова функція: підтримка розширеного кадру CAN-FD */
bool telemetry_send_fd(uint32_t msg_id, const uint8_t *payload, size_t len, uint8_t qos_flags) {
    (void)qos_flags;
    /* Новий контракт підтримує до 64 байтів корисного навантаження */
    return len <= 64;
}
