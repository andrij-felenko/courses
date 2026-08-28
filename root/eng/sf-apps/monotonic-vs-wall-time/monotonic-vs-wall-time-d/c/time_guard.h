/* time_guard.h - C99/C11 cross-platform monotonic time and deadline library */
#ifndef TIME_GUARD_H
#define TIME_GUARD_H

#include <stdint.h>
#include <stdbool.h>

#if defined(_WIN32)
    #include <windows.h>
#elif defined(__APPLE__)
    #include <mach/mach_time.h>
    #include <time.h>
#else
    #include <time.h>
#endif

typedef struct {
    uint64_t start_ns;
    uint64_t timeout_ns;
} deadline_t;

typedef struct {
    uint64_t next_tick_ns;
    uint64_t period_ns;
} ticker_t;

/* Отримання поточного монотонного часу в наносекундах */
static inline uint64_t time_monotonic_ns(void) {
#if defined(_WIN32)
    static LARGE_INTEGER freq;
    static bool init = false;
    if (!init) {
        QueryPerformanceFrequency(&freq);
        init = true;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000000000ULL) / freq.QuadPart);
#elif defined(__APPLE__)
    static mach_timebase_info_data_t tb;
    if (tb.denom == 0) {
        mach_timebase_info(&tb);
    }
    uint64_t t = mach_continuous_time();
    return (t * tb.numer) / tb.denom;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
#endif
}

/* Ініціалізація дедлайну на N мілісекунд уперед */
static inline deadline_t deadline_init_ms(uint64_t timeout_ms) {
    deadline_t d;
    d.start_ns = time_monotonic_ns();
    d.timeout_ns = timeout_ms * 1000000ULL;
    return d;
}

/* Перевірка, чи вичерпано дедлайн */
static inline bool deadline_is_expired(const deadline_t* d) {
    uint64_t now = time_monotonic_ns();
    uint64_t elapsed = (now >= d->start_ns) ? (now - d->start_ns) : 0;
    return elapsed >= d->timeout_ns;
}

/* Скільки мілісекунд залишилося (з насиченням до 0) */
static inline uint64_t deadline_remaining_ms(const deadline_t* d) {
    uint64_t now = time_monotonic_ns();
    uint64_t elapsed = (now >= d->start_ns) ? (now - d->start_ns) : 0;
    if (elapsed >= d->timeout_ns) {
        return 0;
    }
    return (d->timeout_ns - elapsed) / 1000000ULL;
}

/* Ініціалізація періодичного тикера */
static inline ticker_t ticker_init_ms(uint64_t period_ms) {
    ticker_t t;
    t.period_ns = period_ms * 1000000ULL;
    t.next_tick_ns = time_monotonic_ns() + t.period_ns;
    return t;
}

/* Очікування наступного періоду без накопичення похибки фази */
static inline bool ticker_poll(ticker_t* t) {
    uint64_t now = time_monotonic_ns();
    if (now >= t->next_tick_ns) {
        // Додаємо період до запланованої мітки, а не до now!
        t->next_tick_ns += t->period_ns;
        // Захист від відставання при тривалому блокуванні
        if (now >= t->next_tick_ns) {
            t->next_tick_ns = now + t->period_ns;
        }
        return true;
    }
    return false;
}

#endif /* TIME_GUARD_H */
