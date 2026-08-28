#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define ML_MODEL_A_ADDR     0x080D8000U
#define ML_MODEL_B_ADDR     0x08158000U
#define ML_METADATA_ADDR    0x080D0000U
#define ML_MAX_ARENA_SIZE   (48U * 1024U)

typedef struct {
    float primary_prediction;
    float shadow_prediction;
    float absolute_divergence;
    bool  shadow_valid;
} ml_shadow_result_t;

/* Структура контексту виконання */
typedef struct {
    uint32_t active_base_addr;
    uint32_t shadow_base_addr;
    bool shadow_mode_active;
    uint32_t consecutive_valid_cycles;
} ml_runtime_manager_t;

/* Ініціалізація менеджеру за даними метаданих Flash */
bool ml_runtime_init(ml_runtime_manager_t *mgr, uint8_t active_slot, bool enable_shadow) {
    if (!mgr) return false;

    if (active_slot == 0) {
        mgr->active_base_addr = ML_MODEL_A_ADDR;
        mgr->shadow_base_addr = ML_MODEL_B_ADDR;
    } else {
        mgr->active_base_addr = ML_MODEL_B_ADDR;
        mgr->shadow_base_addr = ML_MODEL_A_ADDR;
    }

    mgr->shadow_mode_active = enable_shadow;
    mgr->consecutive_valid_cycles = 0;
    return true;
}

/* Імітація виклику інтерпретатора TFLM для конкретного банку Flash */
static bool invoke_model_inference(uint32_t model_addr, const int8_t *input, float *output_score) {
    if (!input || !output_score) return false;

    /* Зчитування заголовка для отримання зміщення тіла FlatBuffer */
    const uint32_t payload_offset = 128U;
    const uint8_t *flatbuffer_data = (const uint8_t*)(model_addr + payload_offset);

    /* Перевірка валідності покажчика FlatBuffer */
    if (flatbuffer_data[4] != 'T' || flatbuffer_data[5] != 'F' ||
        flatbuffer_data[6] != 'L' || flatbuffer_data[7] != '3') {
        return false; /* Некоректний ідентифікатор FlatBuffer */
    }

    /* Розрахунок класифікації на основі квантованого вхідного вектора */
    float accumulator = 0.0f;
    for (int i = 0; i < 32; ++i) {
        accumulator += (float)input[i] * 0.03125f;
    }

    *output_score = 1.0f / (1.0f + expf(-accumulator));
    return !isnan(*output_score);
}

/* Виконання одного такту інференсу з тіньовим аудитом */
bool ml_runtime_step(ml_runtime_manager_t *mgr,
                    const int8_t *sensor_data,
                    ml_shadow_result_t *result) {
    if (!mgr || !sensor_data || !result) return false;

    /* 1. Інференс основної моделі (керує актуатором) */
    if (!invoke_model_inference(mgr->active_base_addr, sensor_data, &result->primary_prediction)) {
        return false;
    }

    result->shadow_valid = false;
    result->shadow_prediction = 0.0f;
    result->absolute_divergence = 0.0f;

    /* 2. Тіньовий інференс кандидатного банку (якщо активний) */
    if (mgr->shadow_mode_active) {
        if (invoke_model_inference(mgr->shadow_base_addr, sensor_data, &result->shadow_prediction)) {
            result->shadow_valid = true;
            result->absolute_divergence = fabsf(result->primary_prediction - result->shadow_prediction);

            if (result->absolute_divergence < 0.25f) {
                mgr->consecutive_valid_cycles++;
            } else {
                mgr->consecutive_valid_cycles = 0; /* Скидання при значній розбіжності */
            }
        }
    }

    return true;
}
