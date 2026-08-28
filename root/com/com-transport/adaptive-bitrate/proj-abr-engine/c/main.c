#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define ABR_MAX_PROFILES 16
#define ABR_WINDOW_SIZE  5

typedef struct {
    double bytes;
    double duration_sec;
} abr_sample_t;

typedef struct {
    double bitrate_bps;
    int width;
    int height;
} abr_profile_t;

typedef struct {
    abr_profile_t profiles[ABR_MAX_PROFILES];
    size_t profile_count;
    
    // Параметри буфера (в секундах)
    double reservoir_sec;
    double cushion_sec;
    double max_buffer_sec;
    
    // Історія вимірювань каналу
    abr_sample_t window[ABR_WINDOW_SIZE];
    size_t window_head;
    size_t window_count;
    
    double smoothed_throughput_bps;
    size_t current_profile_idx;
    bool in_startup;
} abr_engine_t;

// Ініціалізація рушія ABR
bool abr_engine_init(abr_engine_t *engine, const abr_profile_t *profiles, size_t count,
                     double reservoir, double cushion, double max_buf) {
    if (!engine || !profiles || count == 0 || count > ABR_MAX_PROFILES) {
        return false;
    }
    engine->profile_count = count;
    for (size_t i = 0; i < count; ++i) {
        engine->profiles[i] = profiles[i];
    }
    engine->reservoir_sec = reservoir;
    engine->cushion_sec = cushion;
    engine->max_buffer_sec = max_buf;
    engine->window_head = 0;
    engine->window_count = 0;
    engine->smoothed_throughput_bps = profiles[0].bitrate_bps;
    engine->current_profile_idx = 0;
    engine->in_startup = true;
    return true;
}

// Додавання телеметрії завантаженого сегмента
void abr_engine_add_sample(abr_engine_t *engine, double bytes, double duration_sec) {
    if (!engine || duration_sec <= 0.001 || bytes <= 0.0) return;

    engine->window[engine->window_head].bytes = bytes;
    engine->window[engine->window_head].duration_sec = duration_sec;
    engine->window_head = (engine->window_head + 1) % ABR_WINDOW_SIZE;
    if (engine->window_count < ABR_WINDOW_SIZE) {
        engine->window_count++;
    }

    // Обчислення гармонійного середнього за ковзним вікном:
    // T_harm = Total_Bytes / Total_Duration
    double total_bytes = 0.0;
    double total_duration = 0.0;
    for (size_t i = 0; i < engine->window_count; ++i) {
        total_bytes += engine->window[i].bytes;
        total_duration += engine->window[i].duration_sec;
    }
    double inst_throughput_bps = (total_bytes * 8.0) / total_duration;

    // Експоненційне згладжування EWMA (α = 0.85)
    double alpha = 0.85;
    if (engine->window_count == 1) {
        engine->smoothed_throughput_bps = inst_throughput_bps;
    } else {
        engine->smoothed_throughput_bps = alpha * inst_throughput_bps + (1.0 - alpha) * engine->smoothed_throughput_bps;
    }
}

// Вибір профілю якості для наступного сегмента
size_t abr_engine_select_profile(abr_engine_t *engine, double current_buffer_sec) {
    if (!engine || engine->profile_count == 0) return 0;

    double min_rate = engine->profiles[0].bitrate_bps;
    double max_rate = engine->profiles[engine->profile_count - 1].bitrate_bps;

    // 1. Фаза швидкого старту: агресивне подвоєння якості, поки буфер не наповниться
    if (engine->in_startup) {
        if (current_buffer_sec >= (engine->reservoir_sec + engine->cushion_sec * 0.5)) {
            engine->in_startup = false;
        } else {
            // Обираємо максимальний бітрейт під 75% поточної швидкості
            size_t best = 0;
            double safe_tp = engine->smoothed_throughput_bps * 0.75;
            for (size_t i = 0; i < engine->profile_count; ++i) {
                if (engine->profiles[i].bitrate_bps <= safe_tp) {
                    best = i;
                }
            }
            engine->current_profile_idx = best;
            return best;
        }
    }

    // 2. Стаціонарний режим: функція відображення BBA f(B)
    double target_bitrate;
    if (current_buffer_sec <= engine->reservoir_sec) {
        target_bitrate = min_rate;
    } else if (current_buffer_sec >= (engine->reservoir_sec + engine->cushion_sec)) {
        target_bitrate = max_rate;
    } else {
        double factor = (current_buffer_sec - engine->reservoir_sec) / engine->cushion_sec;
        target_bitrate = min_rate + factor * (max_rate - min_rate);
    }

    // 3. Захисний обмежувач за пропускною здатністю (Safety Clamp 85%)
    double throughput_cap = engine->smoothed_throughput_bps * 0.85;
    if (target_bitrate > throughput_cap) {
        target_bitrate = throughput_cap;
    }

    // 4. Квантування до найближчого дискретного профілю з гістерезисом
    size_t candidate_idx = 0;
    for (size_t i = 0; i < engine->profile_count; ++i) {
        if (engine->profiles[i].bitrate_bps <= target_bitrate) {
            candidate_idx = i;
        }
    }

    // Захист від занадто різкого перемикання вгору (не більше +1 щабля за крок)
    if (candidate_idx > engine->current_profile_idx + 1) {
        candidate_idx = engine->current_profile_idx + 1;
    }

    engine->current_profile_idx = candidate_idx;
    return candidate_idx;
}
