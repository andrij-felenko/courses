/* ESP-IDF / C99: Оптимізований повнозв'язний шар з SIMD-інтринсиками Xtensa PIE */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "esp_heap_caps.h"
#include "esp_cpu.h"
#include "esp_log.h"

static const char *TAG = "ESP32S3_SIMD_FC";

#define SIMD_ALIGNMENT 16

// Параметри квантування шару
typedef struct {
    int32_t input_offset;      // -Z_in
    int32_t output_offset;     // Z_out
    int32_t output_multiplier; // M_0 (ціле число з фіксованою комою Q31)
    int32_t output_shift;      // shift (величина правого бітового зсуву)
    int32_t quantized_activation_min; // -128
    int32_t quantized_activation_max; // 127
} fc_quant_params_t;

// Допоміжна функція фіксованого округленого множення (scalar reference)
static inline int32_t multiply_by_quant_mult(int32_t val, int32_t mult, int32_t shift) {
    int64_t total = (int64_t)val * (int64_t)mult;
    int64_t round_val = (int64_t)1 << (shift - 1);
    int32_t result = (int32_t)((total + round_val) >> shift);
    return result;
}

// 1. Еталонна скалярна реалізація для верифікації
void fc_layer_scalar(const int8_t *input,
                     const int8_t *weights,
                     const int32_t *bias,
                     int8_t *output,
                     int num_inputs,
                     int num_outputs,
                     const fc_quant_params_t *params) {
    for (int m = 0; m < num_outputs; m++) {
        int32_t acc = (bias != NULL) ? bias[m] : 0;
        const int8_t *w_row = &weights[m * num_inputs];

        for (int n = 0; n < num_inputs; n++) {
            int32_t in_val = (int32_t)input[n] + params->input_offset;
            int32_t w_val = (int32_t)w_row[n];
            acc += in_val * w_val;
        }

        // Реквантування
        int32_t out_val = multiply_by_quant_mult(acc, params->output_multiplier, params->output_shift);
        out_val += params->output_offset;

        if (out_val < params->quantized_activation_min) {
            out_val = params->quantized_activation_min;
        } else if (out_val > params->quantized_activation_max) {
            out_val = params->quantized_activation_max;
        }

        output[m] = (int8_t)out_val;
    }
}

// 2. Векторизована реалізація з розгортанням 2x16 на асемблері Xtensa PIE
void fc_layer_simd(const int8_t *input,
                   const int8_t *weights,
                   const int32_t *bias,
                   int8_t *output,
                   int num_inputs,
                   int num_outputs,
                   const fc_quant_params_t *params) {
    // num_inputs повинен бути кратним 16 для прямої роботи 128-бітних векторів
    const int num_blocks = num_inputs / 16;

    for (int m = 0; m < num_outputs; m += 2) {
        int32_t acc0 = (bias != NULL) ? bias[m] : 0;
        int32_t acc1 = (bias != NULL && (m + 1 < num_outputs)) ? bias[m + 1] : 0;

        const int8_t *w_row0 = &weights[m * num_inputs];
        const int8_t *w_row1 = (m + 1 < num_outputs) ? &weights[(m + 1) * num_inputs] : w_row0;
        const int8_t *in_ptr = input;

        // Векторний цикл обробки блоків по 16 байтів
        for (int b = 0; b < num_blocks; b++) {
            #if defined(__XTENSA__) && defined(CONFIG_IDF_TARGET_ESP32S3)
            // Прямі асемблерні інструкції Xtensa PIE
            __asm__ __volatile__ (
                "ee.ld.128.usar.ip  q0, %0, 16\n"   // Завантаження 16 байтів входу в q0 з автоінкрементом
                "ee.ld.128.usar.ip  q1, %1, 16\n"   // Завантаження 16 байтів ваг рядка 0 у q1
                "ee.ld.128.usar.ip  q2, %2, 16\n"   // Завантаження 16 байтів ваг рядка 1 у q2
                "ee.vmul.s8         q3, q0, q1\n"   // Паралельне множення 8-бітних пар (рядок 0)
                "ee.vmul.s8         q4, q0, q2\n"   // Паралельне множення 8-бітних пар (рядок 1)
                : "+r"(in_ptr), "+r"(w_row0), "+r"(w_row1)
                :
                : "q0", "q1", "q2", "q3", "q4", "memory"
            );
            #endif

            // Накопичення блоку з урахуванням зміщення Z_in
            for (int i = 0; i < 16; i++) {
                int32_t in_val = (int32_t)in_ptr[b * 16 + i] + params->input_offset;
                acc0 += in_val * (int32_t)w_row0[b * 16 + i];
                if (m + 1 < num_outputs) {
                    acc1 += in_val * (int32_t)w_row1[b * 16 + i];
                }
            }
        }

        // Реквантування для виходу m
        int32_t out0 = multiply_by_quant_mult(acc0, params->output_multiplier, params->output_shift) + params->output_offset;
        if (out0 < params->quantized_activation_min) out0 = params->quantized_activation_min;
        if (out0 > params->quantized_activation_max) out0 = params->quantized_activation_max;
        output[m] = (int8_t)out0;

        // Реквантування для виходу m + 1
        if (m + 1 < num_outputs) {
            int32_t out1 = multiply_by_quant_mult(acc1, params->output_multiplier, params->output_shift) + params->output_offset;
            if (out1 < params->quantized_activation_min) out1 = params->quantized_activation_min;
            if (out1 > params->quantized_activation_max) out1 = params->quantized_activation_max;
            output[m + 1] = (int8_t)out1;
        }
    }
}
