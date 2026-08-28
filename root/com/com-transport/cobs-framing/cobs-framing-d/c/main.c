#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/**
 * Кодування масиву байтів за алгоритмом COBS.
 * @param src Вказівник на вхідний масив корисних даних.
 * @param src_len Довжина вхідного масиву.
 * @param dst Вказівник на вихідний буфер (розмір >= src_len + src_len/254 + 1).
 * @return Кількість записаних байтів у dst (без кінцевого 0x00).
 */
size_t cobs_encode(const uint8_t *src, size_t src_len, uint8_t *dst) {
    if (!src || !dst || src_len == 0) return 0;

    const uint8_t *src_end = src + src_len;
    uint8_t *code_ptr = dst++;
    uint8_t code = 0x01;

    while (src < src_end) {
        if (*src == 0) {
            *code_ptr = code;
            code_ptr = dst++;
            code = 0x01;
            src++;
        } else {
            *dst++ = *src++;
            code++;
            if (code == 0xFF) {
                *code_ptr = code;
                code_ptr = dst++;
                code = 0x01;
            }
        }
    }
    *code_ptr = code;
    return (size_t)(dst - (code_ptr - (code - 1)) + (code == 0x01 ? 0 : 0));
}

/**
 * Декодування масиву COBS. Підтримує роботу in-place (src == dst).
 * @param src Вказівник на закодовані дані (без кінцевого 0x00).
 * @param src_len Довжина закодованих даних.
 * @param dst Вказівник на вихідний буфер.
 * @param out_len Вказівник для збереження довжини відновлених даних.
 * @return true при успішному декодуванні, false при помилці структури кадру.
 */
bool cobs_decode(const uint8_t *src, size_t src_len, uint8_t *dst, size_t *out_len) {
    if (!src || !dst || !out_len || src_len == 0) return false;

    const uint8_t *src_end = src + src_len;
    uint8_t *dst_start = dst;

    while (src < src_end) {
        uint8_t code = *src++;
        if (code == 0) return false; // Помилка: нуль усередині тіла кадру!

        uint8_t copy_len = code - 1;
        if (src + copy_len > src_end) return false; // Покажчик виходить за межі кадру

        while (copy_len--) {
            *dst++ = *src++;
        }

        // Вставляємо неявний нуль, якщо це не блок 0xFF і не кінець кадру
        if (code < 0xFF && src < src_end) {
            *dst++ = 0x00;
        }
    }

    *out_len = (size_t)(dst - dst_start);
    return true;
}
