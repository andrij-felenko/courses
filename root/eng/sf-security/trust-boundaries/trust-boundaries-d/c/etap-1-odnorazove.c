#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define MAX_PAYLOAD_LEN 1024

typedef struct {
    uint32_t length;
    uint8_t data[MAX_PAYLOAD_LEN];
} SafeMessage;

/* Безпечна вибірка: дані копіюються в стек до перевірки інваріантів */
bool fetch_and_validate_message(const void *untrusted_src, size_t raw_size, SafeMessage *out_msg) {
    if (untrusted_src == NULL || out_msg == NULL) {
        return false;
    }
    if (raw_size < sizeof(uint32_t) || raw_size > sizeof(SafeMessage)) {
        return false;
    }

    /* Крок 1: Єдине копіювання всієї структури у локальний буфер */
    SafeMessage local_copy;
    memcpy(&local_copy, untrusted_src, raw_size);

    /* Крок 2: Валідація виключно локальної копії (пам'ять клієнта більше не читається) */
    if (local_copy.length > MAX_PAYLOAD_LEN) {
        return false;
    }
    if (sizeof(uint32_t) + local_copy.length > raw_size) {
        return false;
    }

    /* Крок 3: Передача перевіреного результату */
    memcpy(out_msg, &local_copy, sizeof(SafeMessage));
    return true;
}
