#include "cobs.h"

size_t cobs_max_encoded(size_t len) {
    return len + len / 254U + 1U;
}

bool cobs_encode(const uint8_t *src, size_t src_len,
                 uint8_t *dst, size_t dst_cap, size_t *out_len) {
    if (dst == NULL || out_len == NULL || (src == NULL && src_len != 0U)) {
        return false;
    }
    if (dst_cap == 0U) {
        return false;
    }

    size_t read_i = 0U;
    size_t code_i = 0U;   // місце, зарезервоване під покажчик зміщення групи
    size_t write_i = 1U;
    uint8_t code = 1U;    // зміщення до наступного нуля, рахуючи сам покажчик

    while (read_i < src_len) {
        if (src[read_i] == 0x00U) {
            // Нуль не передається: він перетворюється на довжину щойно закритої групи.
            dst[code_i] = code;
            code = 1U;
            code_i = write_i++;
            if (code_i >= dst_cap) {
                return false;
            }
            ++read_i;
        } else {
            if (write_i >= dst_cap) {
                return false;
            }
            dst[write_i++] = src[read_i++];
            ++code;
            if (code == 0xFFU) {
                // Група досягла 254 ненульових байтів — закриваємо її примусово.
                dst[code_i] = code;
                code = 1U;
                code_i = write_i++;
                if (code_i >= dst_cap) {
                    return false;
                }
            }
        }
    }

    if (code_i >= dst_cap) {
        return false;
    }
    dst[code_i] = code;
    *out_len = write_i;
    return true;
}

bool cobs_decode(const uint8_t *src, size_t src_len,
                 uint8_t *dst, size_t dst_cap, size_t *out_len) {
    if (src == NULL || dst == NULL || out_len == NULL || src_len == 0U) {
        return false;
    }

    size_t src_i = 0U;
    size_t dst_i = 0U;

    while (src_i < src_len) {
        uint8_t code = src[src_i++];
        if (code == 0x00U) {
            return false;   // нуль усередині тіла — кадр структурно зіпсовано
        }

        for (uint8_t i = 1U; i < code; ++i) {
            if (src_i >= src_len || dst_i >= dst_cap) {
                return false;   // зміщення вказує за межі реальних даних
            }
            dst[dst_i++] = src[src_i++];
        }

        // Останню групу нуль не закриває: він і був роздільником кадру.
        if (code < 0xFFU && src_i < src_len) {
            if (dst_i >= dst_cap) {
                return false;
            }
            dst[dst_i++] = 0x00U;
        }
    }

    *out_len = dst_i;
    return true;
}
