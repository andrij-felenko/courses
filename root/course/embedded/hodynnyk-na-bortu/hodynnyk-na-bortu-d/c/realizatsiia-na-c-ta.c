#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TIME_SLEW_MAX_PPM        500     // Максимальний зсув частоти slew (+-500 ppm = +-0.05%)
#define TIME_STEP_THRESHOLD_US   2000000 // Поріг 2 секунди: більше -> step, менше -> slew
#define PPM_SCALE                1000000

typedef struct {
    // Атомарна версія для блокування читання без блокувань (Seqlock)
    volatile uint32_t sequence;

    // Стан апаратного монотонного лічильника
    uint32_t last_hw_ticks;
    uint64_t monotonic_accum_us;

    // Зсув настінного часу відносно монотонного (UTC epoch)
    int64_t epoch_offset_us;

    // Стан плавного підтягування (Slew)
    int64_t  slew_remaining_us;    // Залишок похибки, яку треба плавно вибрати
    int32_t  slew_rate_ppm;        // Поточна швидкість підтягування (+-500 ppm)
    uint64_t last_slew_update_us;  // Час останнього перерахунку slew

    // Коефіцієнти калібрування дрейфу кварцу
    int32_t  static_drift_ppm;
} system_time_engine_t;

static system_time_engine_t g_time_engine;

// Зовнішня функція апаратного таймера (наприклад, SysTick або TIMx 1 МГц)
extern uint32_t hw_timer_get_32bit_ticks(void);

void time_engine_init(int64_t initial_utc_us, int32_t quartz_drift_ppm) {
    g_time_engine.sequence = 0;
    g_time_engine.last_hw_ticks = hw_timer_get_32bit_ticks();
    g_time_engine.monotonic_accum_us = 0;
    g_time_engine.epoch_offset_us = initial_utc_us;
    g_time_engine.slew_remaining_us = 0;
    g_time_engine.slew_rate_ppm = 0;
    g_time_engine.last_slew_update_us = 0;
    g_time_engine.static_drift_ppm = quartz_drift_ppm;
}

// Оновлення накопичувача (викликається періодично або перед читанням)
static void time_engine_update_internal(void) {
    uint32_t current_ticks = hw_timer_get_32bit_ticks();
    uint32_t delta_ticks = current_ticks - g_time_engine.last_hw_ticks;
    g_time_engine.last_hw_ticks = current_ticks;

    // Додаємо дельту до монотонного лічильника
    g_time_engine.monotonic_accum_us += (uint64_t)delta_ticks;
    uint64_t now_mono = g_time_engine.monotonic_accum_us;

    // Обробка плавного підтягування (Slew)
    if (g_time_engine.slew_remaining_us != 0) {
        uint64_t dt = now_mono - g_time_engine.last_slew_update_us;
        if (dt > 0) {
            // Скільки мікросекунд коригування набігло за проміжок dt
            int64_t delta_slew = ((int64_t)dt * g_time_engine.slew_rate_ppm) / PPM_SCALE;

            // Перевірка на досягнення цілі
            if ((g_time_engine.slew_remaining_us > 0 && delta_slew >= g_time_engine.slew_remaining_us) ||
                (g_time_engine.slew_remaining_us < 0 && delta_slew <= g_time_engine.slew_remaining_us)) {
                g_time_engine.epoch_offset_us += g_time_engine.slew_remaining_us;
                g_time_engine.slew_remaining_us = 0;
                g_time_engine.slew_rate_ppm = 0;
            } else {
                g_time_engine.epoch_offset_us += delta_slew;
                g_time_engine.slew_remaining_us -= delta_slew;
            }
            g_time_engine.last_slew_update_us = now_mono;
        }
    }
}

// Отримання строго монотонного часу (ніколи не йде назад)
uint64_t time_get_monotonic_us(void) {
    uint32_t seq;
    uint64_t mono;

    do {
        seq = g_time_engine.sequence;
        // Seqlock: непарне число означає, що триває оновлення структури
        while (seq & 1) {
            seq = g_time_engine.sequence;
        }
        
        // Враховуємо поточний стан лічильника
        uint32_t current_ticks = hw_timer_get_32bit_ticks();
        uint32_t delta = current_ticks - g_time_engine.last_hw_ticks;
        mono = g_time_engine.monotonic_accum_us + delta;

    } while (g_time_engine.sequence != seq);

    return mono;
}

// Отримання настінного часу UTC
int64_t time_get_wall_clock_utc_us(void) {
    uint32_t seq;
    int64_t wall;

    do {
        seq = g_time_engine.sequence;
        while (seq & 1) {
            seq = g_time_engine.sequence;
        }
        
        uint64_t mono = time_get_monotonic_us();
        wall = (int64_t)mono + g_time_engine.epoch_offset_us;

    } while (g_time_engine.sequence != seq);

    return wall;
}

// Синхронізація часу від сервера (NTP / GPS)
void time_sync_adjust(int64_t target_utc_us) {
    // Вхід у критичну секцію Seqlock
    g_time_engine.sequence++;
    __asm__ volatile("" ::: "memory"); // Бар'єр пам'яті

    time_engine_update_internal();

    int64_t current_utc = (int64_t)g_time_engine.monotonic_accum_us + g_time_engine.epoch_offset_us;
    int64_t phase_error = target_utc_us - current_utc;

    // Якщо похибка величезна — робимо миттєвий крок (Step)
    if (phase_error > TIME_STEP_THRESHOLD_US || phase_error < -TIME_STEP_THRESHOLD_US) {
        g_time_engine.epoch_offset_us += phase_error;
        g_time_engine.slew_remaining_us = 0;
        g_time_engine.slew_rate_ppm = 0;
    } else {
        // Плавне підтягування (Slew): обмежуємо темп +-500 ppm
        g_time_engine.slew_remaining_us = phase_error;
        g_time_engine.slew_rate_ppm = (phase_error > 0) ? TIME_SLEW_MAX_PPM : -TIME_SLEW_MAX_PPM;
        g_time_engine.last_slew_update_us = g_time_engine.monotonic_accum_us;
    }

    __asm__ volatile("" ::: "memory");
    g_time_engine.sequence++; // Завершення критичної секції (число знову парне)
}
