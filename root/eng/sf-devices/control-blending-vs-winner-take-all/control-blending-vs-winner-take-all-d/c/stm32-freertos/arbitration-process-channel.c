#include <stdint.h>
#include <stdbool.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

#define Q16_SHIFT           16
#define Q16_ONE             (1L << Q16_SHIFT)
#define HYSTERESIS_HIGH_Q16 ((int32_t)(0.75f * Q16_ONE))
#define HYSTERESIS_LOW_Q16  ((int32_t)(0.25f * Q16_ONE))

typedef enum {
    ARBITRATION_MODE_BLENDING = 0,
    ARBITRATION_MODE_WINNER_TAKE_ALL = 1
} arbitration_mode_t;

typedef struct {
    int32_t primary_cmd_q16;
    int32_t secondary_cmd_q16;
    int32_t primary_weight_q16;
    int32_t max_slew_rate_q16;
    int32_t min_output_limit_q16;
    int32_t max_output_limit_q16;
    int32_t last_output_q16;
    arbitration_mode_t current_mode;
} arbitration_channel_t;

// Атомна обробка арбітражу з опуклою комбінацією та витісненням
int32_t arbitration_process_channel(arbitration_channel_t *channel) {
    int32_t raw_output_q16 = 0;

    // Гістерезисна петля перемикання режимів
    if (channel->current_mode == ARBITRATION_MODE_BLENDING) {
        if (channel->primary_weight_q16 >= HYSTERESIS_HIGH_Q16) {
            channel->current_mode = ARBITRATION_MODE_WINNER_TAKE_ALL;
        }
    } else {
        if (channel->primary_weight_q16 < HYSTERESIS_LOW_Q16) {
            channel->current_mode = ARBITRATION_MODE_BLENDING;
        }
    }

    // Обчислення виходу залежно від активного режиму
    if (channel->current_mode == ARBITRATION_MODE_WINNER_TAKE_ALL) {
        // Витіснення (winner-take-all): повний пріоритет первинного джерела
        raw_output_q16 = channel->primary_cmd_q16;
    } else {
        // Злиття керування (control blending): опукла комбінація в Q16.16
        // y = u2 + w1 * (u1 - u2)
        int64_t diff = (int64_t)channel->primary_cmd_q16 - channel->secondary_cmd_q16;
        int64_t blended_diff = (diff * channel->primary_weight_q16) >> Q16_SHIFT;
        raw_output_q16 = channel->secondary_cmd_q16 + (int32_t)blended_diff;
    }

    // Обмежувач швидкості зміни (slew rate limiter)
    int32_t delta = raw_output_q16 - channel->last_output_q16;
    if (delta > channel->max_slew_rate_q16) {
        raw_output_q16 = channel->last_output_q16 + channel->max_slew_rate_q16;
    } else if (delta < -channel->max_slew_rate_q16) {
        raw_output_q16 = channel->last_output_q16 - channel->max_slew_rate_q16;
    }

    // Проектор меж безпеки (safety bounds projector)
    if (raw_output_q16 > channel->max_output_limit_q16) {
        raw_output_q16 = channel->max_output_limit_q16;
    } else if (raw_output_q16 < channel->min_output_limit_q16) {
        raw_output_q16 = channel->min_output_limit_q16;
    }

    channel->last_output_q16 = raw_output_q16;
    return raw_output_q16;
}
