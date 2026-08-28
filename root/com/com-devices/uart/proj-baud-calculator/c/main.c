#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stddef.h>

/* Конфігураційне зведення дільника UART */
typedef struct {
    uint32_t brr_value;       /* Значення для запису в регістр BRR */
    uint32_t actual_baud;     /* Фактична згенерована швидкість */
    float error_percent;      /* Відсоток похибки відносно цілі */
    uint8_t oversampling;     /* Використаний коефіцієнт (16 або 8) */
    bool is_valid;            /* true, якщо похибка у межах ±2.5% */
} uart_baud_config_t;

/**
 * @brief Обчислює значення регістра BRR для UART з перевіркою похибки
 * @param pclk_hz Частота тактування периферійної шини у Гц
 * @param target_baud Бажана швидкість передачі в біт/с
 * @param allow_oversample8 Дозвіл перемикання на 8x oversampling при високій похибці
 * @param out_config Вказівник на структуру для збереження результату
 * @return true при успішному розрахунку, false при некоректних вхідних даних
 */
bool uart_calculate_brr(uint32_t pclk_hz, uint32_t target_baud, bool allow_oversample8, uart_baud_config_t *out_config) {
    if (pclk_hz == 0 || target_baud == 0 || out_config == NULL) {
        return false;
    }

    uint8_t selected_oversample = 16;
    uint32_t mantissa = 0;
    uint32_t fraction = 0;
    float best_error = 100.0f;
    uint32_t best_brr = 0;
    uint32_t best_actual_baud = 0;

    /* Пробуємо 16x oversampling, а при необхідності — 8x */
    for (uint8_t os = 16; os >= 8; os -= 8) {
        if (os == 8 && !allow_oversample8) {
            break;
        }

        /* USARTDIV = pclk_hz / (os * target_baud) */
        float usartdiv = (float)pclk_hz / (float)(os * target_baud);
        uint32_t m = (uint32_t)floorf(usartdiv);
        float frac_part = usartdiv - (float)m;

        uint32_t f = 0;
        if (os == 16) {
            f = (uint32_t)roundf(frac_part * 16.0f);
            if (f >= 16) { f = 0; m += 1; }
        } else {
            f = (uint32_t)roundf(frac_part * 8.0f);
            if (f >= 8) { f = 0; m += 1; }
        }

        /* Перевірка меж мантіси */
        if (m == 0 || m > 0xFFFF) {
            continue;
        }

        /* Фактичний дільник і швидкість */
        float div_actual = (os == 16) ? ((float)m + ((float)f / 16.0f)) : ((float)m + ((float)f / 8.0f));
        uint32_t actual_baud = (uint32_t)roundf((float)pclk_hz / ((float)os * div_actual));

        float error = fabsf(((float)actual_baud - (float)target_baud) / (float)target_baud) * 100.0f;

        if (error < best_error) {
            best_error = error;
            best_actual_baud = actual_baud;
            selected_oversample = os;
            if (os == 16) {
                best_brr = (m << 4) | (f & 0x0F);
            } else {
                /* Для 8x фракція пакується в 3 біти (0..2) */
                best_brr = (m << 4) | (f & 0x07);
            }
        }

        if (best_error <= 2.5f) {
            break; /* Допустима похибка досягнута */
        }
    }

    out_config->brr_value = best_brr;
    out_config->actual_baud = best_actual_baud;
    out_config->error_percent = best_error;
    out_config->oversampling = selected_oversample;
    out_config->is_valid = (best_error <= 2.5f);

    return out_config->is_valid;
}
